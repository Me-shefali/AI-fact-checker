import httpx
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()

import wikipedia
import wikipediaapi
from ddgs import DDGS
from sentence_transformers import CrossEncoder, SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from services.nlp_model import nlp

# ── Models ───────────────────────────────────────────────────────────
# MiniLM  → retrieval only: ranks which evidence snippets are most
#            topically relevant to fetch. Never used in verdict logic.
# NLI     → verdict only:   reads claim + evidence together and decides
#            entailment / contradiction / neutral contextually.
#            This is the ONLY model that determines True/False/Unverified.
nli_model   = CrossEncoder("MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Label order for MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli
LABEL_CONTRADICTION = 0
LABEL_NEUTRAL       = 1
LABEL_ENTAILMENT    = 2

# Source weights applied ONLY to NLI output scores — not to retrieval
SOURCE_WEIGHTS = {
    "Google Fact Check": 1.5,
    "Wikipedia":         1.0,
    "Web":               0.7,
}

GOOGLE_FC_API_KEY = os.getenv("GOOGLE_FC_API_KEY")


# ── 1. Google Fact Check ──────────────────────────────────────────────
def search_google_factcheck(claim: str) -> list[dict]:
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": claim, "key": GOOGLE_FC_API_KEY, "languageCode": "en"}
    try:
        r = httpx.get(url, params=params, timeout=8)
        data = r.json()
        results = []
        for item in data.get("claims", [])[:3]:
            for review in item.get("claimReview", []):
                results.append({
                    "text": f"{item.get('text', '')} — Rating: {review.get('textualRating', '')}",
                    "url": review.get("url", ""),
                    "source": review.get("publisher", {}).get("name", "Google Fact Check")
                })
        return results
    except Exception:
        return []


# ── 2. Wikipedia ──────────────────────────────────────────────────────
def search_wikipedia(claim: str) -> list[dict]:
    results = []
    seen_urls = set()
    wiki_api = wikipediaapi.Wikipedia(user_agent="FactChecker/1.0", language="en")

    def add_page(page):
        if page.exists() and page.fullurl not in seen_urls:
            seen_urls.add(page.fullurl)
            results.append({
                "text": page.summary[:1000],
                "url": page.fullurl,
                "source": "Wikipedia"
            })

    # Path A: full claim search
    try:
        for title in wikipedia.search(claim, results=5)[:5]:
            try:
                add_page(wiki_api.page(title))
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
    except Exception:
        pass

    # Path B: per-entity/noun-chunk direct lookup
    # Handles cases where full-claim search returns off-topic pages
    try:
        doc = nlp(claim)
        entities = [ent.text for ent in doc.ents]
        if not entities:
            entities = [chunk.text for chunk in doc.noun_chunks]

        for kw in entities[:4]:
            try:
                add_page(wiki_api.page(kw))
                for title in wikipedia.search(kw, results=2)[:2]:
                    try:
                        add_page(wiki_api.page(title))
                    except (wikipedia.DisambiguationError, wikipedia.PageError):
                        continue
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
    except Exception:
        pass

    return results


# ── 3. DuckDuckGo ─────────────────────────────────────────────────────
def search_duckduckgo(claim: str) -> list[dict]:
    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(claim, max_results=5))
        return [
            {"text": h.get("body", ""), "url": h.get("href", ""), "source": "Web"}
            for h in hits if h.get("body")
        ]
    except Exception:
        return []


# ── 4. MiniLM retrieval ranker ────────────────────────────────────────
def retrieve_top_evidence(claim: str, evidence_list: list[dict], top_k: int = 8) -> list[dict]:
    """
    MiniLM's ONLY job: rank evidence by topical relevance and return top_k.

    It does NOT determine the verdict. It does NOT filter by a similarity
    threshold that could cut good evidence. It simply sorts and returns
    the most topically relevant snippets for the NLI model to read.

    Source weight is applied here only to prevent short authoritative
    Google FC snippets from being ranked below longer Wikipedia pages
    on pure cosine similarity alone.
    """
    if not evidence_list:
        return []

    texts = [e["text"] for e in evidence_list if e.get("text")]
    if not texts:
        return []

    claim_vec     = embed_model.encode([claim])
    evidence_vecs = embed_model.encode(texts)
    sims          = cosine_similarity(claim_vec, evidence_vecs)[0]

    # Rank by similarity × source weight — retrieval order only
    ranked = sorted(
        zip(sims.tolist(), evidence_list),
        key=lambda x: x[0] * SOURCE_WEIGHTS.get(x[1].get("source", "Web"), 0.7),
        reverse=True
    )

    # Return top_k regardless of score — no threshold cutoff.
    # If there is no relevant evidence at all, that is NLI's problem
    # to decide, not MiniLM's job to hide from NLI.
    return [e for _, e in ranked[:top_k]]


# ── 5. Softmax ────────────────────────────────────────────────────────
def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)


# ── 6. NLI contextual scoring ────────────────────────────────────────
def score_with_nli(claim: str, evidence_list: list[dict]) -> list[dict]:
    """
    NLI's ONLY job: read each (claim, evidence) pair together and output
    entailment / contradiction / neutral probabilities.

    This is purely contextual — the model reads the full text of both
    the claim and the evidence and decides the logical relationship.
    Similarity plays NO role here whatsoever.

    Source weight is applied to the NLI output scores only to reflect
    that a Google FC verdict is more authoritative than a Wikipedia
    general summary or a DDG web snippet.
    """
    if not evidence_list:
        return []

    pairs = [(claim, e["text"]) for e in evidence_list if e.get("text")]
    if not pairs:
        return []

    raw_logits = nli_model.predict(pairs)
    if raw_logits.ndim == 1:
        raw_logits = raw_logits.reshape(1, -1)

    # Softmax converts logits to proper probabilities summing to 1.0
    probs = softmax(raw_logits)

    scored = []
    for i, e in enumerate(evidence_list):
        if not e.get("text"):
            continue
        weight = SOURCE_WEIGHTS.get(e.get("source", "Web"), 0.7)
        # Raw probabilities stored separately for unbiased gating
        scored.append({
            **e,
            "entail_prob":  float(probs[i, LABEL_ENTAILMENT]),
            "contra_prob":  float(probs[i, LABEL_CONTRADICTION]),
            "neutral_prob": float(probs[i, LABEL_NEUTRAL]),
            # Weighted scores for aggregation — source authority amplifies
            "entail_weighted": float(probs[i, LABEL_ENTAILMENT])   * weight,
            "contra_weighted": float(probs[i, LABEL_CONTRADICTION]) * weight,
        })
    return scored


# ── 7. Verdict — purely NLI contextual output ─────────────────────────
def decide_verdict(nli_scored: list[dict]) -> tuple[str, float, list]:
    """
    Decides verdict based purely on NLI contextual scores.
    No similarity involved. No MiniLM scores here.

    Strategy:
    - Take the single best entailment score and single best contradiction
      score across all evidence snippets (max).
    - Also compute mean to require some consensus, not just one lucky hit.
    - Combined = 60% max + 40% mean.
    - Whichever is higher (entail vs contra) wins, subject to a minimum
      threshold to avoid noise producing confident wrong verdicts.

    The threshold 0.25 on combined weighted scores is intentionally low
    because source weighting already amplifies reliable sources. A Google FC
    snippet at 0.5 raw × 1.5 weight = 0.75 weighted — easily clears 0.25.
    A Wikipedia summary at 0.35 raw × 1.0 weight = 0.35 — also clears it.
    Only truly neutral/irrelevant evidence (e.g. 0.15 raw × 0.7 = 0.105)
    stays below threshold and correctly produces Unverified.
    """
    if not nli_scored:
        return "Unverified", 0.0, []

    entail_w = [e["entail_weighted"] for e in nli_scored]
    contra_w = [e["contra_weighted"] for e in nli_scored]

    combined_entail = 0.6 * max(entail_w) + 0.4 * float(np.mean(entail_w))
    combined_contra = 0.6 * max(contra_w) + 0.4 * float(np.mean(contra_w))

    # Verdict: whichever NLI signal is stronger wins
    if combined_entail >= combined_contra:
        if combined_entail > 0.25:
            verdict, confidence = "True", combined_entail
        else:
            verdict, confidence = "Unverified", combined_entail
    else:
        if combined_contra > 0.25:
            verdict, confidence = "False", combined_contra
        else:
            verdict, confidence = "Unverified", combined_contra

    # Return top 2 evidence by entailment (for display)
    top_two = sorted(nli_scored, key=lambda e: e["entail_weighted"], reverse=True)[:2]
    clean_evidence = [
        {"text": e["text"], "url": e["url"], "source": e["source"]}
        for e in top_two
    ]

    return verdict, round(confidence, 3), clean_evidence


# ── Main entry point ──────────────────────────────────────────────────
def verify_claims(claims: list[str]) -> list[dict]:
    results = []

    for claim in claims:
        # Step 1: Gather evidence from all sources
        google_evidence = search_google_factcheck(claim)
        wiki_evidence   = search_wikipedia(claim)
        ddg_evidence    = search_duckduckgo(claim)
        all_evidence    = google_evidence + wiki_evidence + ddg_evidence

        # Step 2: MiniLM ranks by topical relevance — retrieval only
        top_evidence = retrieve_top_evidence(claim, all_evidence, top_k=8)
        if not top_evidence:
            top_evidence = all_evidence[:8]

        # Step 3: NLI reads claim + evidence contextually — verdict only
        nli_scored = score_with_nli(claim, top_evidence)

        # Step 4: Decide verdict from NLI scores alone
        verdict, confidence, used_evidence = decide_verdict(nli_scored)

        results.append({
            "claim":      claim,
            "verdict":    verdict,
            "confidence": round(confidence, 3),
            "similarity": round(confidence, 3),
            "evidence":   used_evidence
        })

    return results