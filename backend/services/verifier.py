import httpx
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()

import wikipedia
import wikipediaapi
from ddgs import DDGS
from sklearn.metrics.pairwise import cosine_similarity

# ── Centralized model imports ─────────────────────────────────────────
# Models are loaded ONCE as singletons in their own files.
# Never instantiate CrossEncoder / SentenceTransformer here.
from services.nlp_model import nlp                       # spaCy en_core_web_sm
from models.nli_model import nli_model                   # DeBERTa NLI CrossEncoder
from models.embedding_model import model as embed_model  # MiniLM SentenceTransformer
from utils.helper import is_readable, build_smart_queries  # helper functions

# ── Constants ─────────────────────────────────────────────────────────
LABEL_CONTRADICTION = 0
LABEL_NEUTRAL       = 1
LABEL_ENTAILMENT    = 2

SOURCE_WEIGHTS = {
    "Google Fact Check": 1.5,
    "Wikipedia":         1.0,
    "Web":               0.7,
}

GOOGLE_FC_API_KEY = os.getenv("GOOGLE_FC_API_KEY")

# Google Fact Check stores the FALSE claim text, so negation claims
# often match the wrong way — reduce its authority for those.
NEGATION_WORDS = {"not", "never", "no", "isn't", "aren't", "wasn't",
                  "weren't", "doesn't", "don't", "didn't", "cannot", "can't"}


# ── Helper: dynamic source weight ────────────────────────────────────
def get_source_weight(source: str, claim: str) -> float:
    base_weight = SOURCE_WEIGHTS.get(source, 0.7)
    if source == "Google Fact Check":
        if set(claim.lower().split()) & NEGATION_WORDS:
            return 0.6   # down from 1.5 for negation claims
    return base_weight

def extract_best_sentence(evidence_text: str, claim: str) -> str:
    """
    Instead of passing the full 1000-char Wikipedia summary to NLI,
    extract just the most relevant sentence. NLI works far better on
    short focused pairs than on long paragraphs.

    e.g. For claim "India is a member of the UN":
    Full summary: "India officially the Republic of India is a country 
                   in South Asia... it is the seventh largest..."
    Best sentence: "India is one of the 51 founding members of the UN."
    """
    doc = nlp(evidence_text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    
    if not sentences:
        return evidence_text[:300]
    
    if len(sentences) == 1:
        return sentences[0]
    
    # Use MiniLM to find the most relevant sentence
    claim_vec    = embed_model.encode([claim])
    sent_vecs    = embed_model.encode(sentences)
    sims         = cosine_similarity(claim_vec, sent_vecs)[0]
    best_idx     = int(np.argmax(sims))
    
    # Return best sentence + neighbour for context
    start = max(0, best_idx - 1)
    end   = min(len(sentences), best_idx + 2)
    return " ".join(sentences[start:end])

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
                    "text":   f"{item.get('text', '')} — Rating: {review.get('textualRating', '')}",
                    "url":    review.get("url", ""),
                    "source": review.get("publisher", {}).get("name", "Google Fact Check"),
                })
        return results
    except Exception:
        return []


# ── 2. Wikipedia REST API — primary search ────────────────────────────
def search_wikipedia_rest(queries: list[str]) -> list[dict]:
    """
    Uses Wikipedia's MediaWiki REST API with focused entity queries.

    Two-step:
      1. Search for matching article titles given the query
      2. Fetch the intro paragraph (extract) of each matched article

    Far more reliable than the python wikipedia library because we
    control exactly what we search for — "Tehran Iran" finds the Tehran
    article which explicitly states it is Iran's capital, rather than a
    generic search that might return unrelated pages.
    """
    results   = []
    seen_urls = set()
    api_url   = "https://en.wikipedia.org/w/api.php"

    for query in queries:
        try:
            # Step 1: find matching titles
            r = httpx.get(api_url, params={
                "action":   "query",
                "list":     "search",
                "srsearch": query,
                "format":   "json",
                "srlimit":  3,
            }, timeout=8)
            titles = [i["title"] for i in r.json().get("query", {}).get("search", [])]

            # Step 2: fetch intro extract for top 2 titles
            for title in titles[:2]:
                page_r = httpx.get(api_url, params={
                    "action":      "query",
                    "titles":      title,
                    "prop":        "extracts|info",
                    "exintro":     True,
                    "explaintext": True,
                    "inprop":      "url",
                    "format":      "json",
                }, timeout=8)
                for page in page_r.json().get("query", {}).get("pages", {}).values():
                    extract  = page.get("extract", "").strip()
                    full_url = page.get("fullurl", "")
                    if extract and full_url and full_url not in seen_urls:
                        seen_urls.add(full_url)
                        results.append({
                            "text":   extract[:1000],
                            "url":    full_url,
                            "source": "Wikipedia",
                        })
        except Exception:
            continue

    return results


# ── 3. Wikipedia library — fallback search ────────────────────────────
def search_wikipedia_fallback(claim: str) -> list[dict]:
    """
    Fallback using the python wikipedia library.
    Catches pages the REST API might miss, especially for broad claims
    where no clean entity pair is available.
    No hardcoded disambiguation dictionary — the REST API with smart
    queries already handles that; this fallback searches entity names directly.
    """
    results   = []
    seen_urls = set()
    wiki_api  = wikipediaapi.Wikipedia(user_agent="FactChecker/1.0", language="en")

    def add_page(page):
        if page.exists() and page.fullurl not in seen_urls:
            seen_urls.add(page.fullurl)
            results.append({
                "text":   page.summary[:1000],
                "url":    page.fullurl,
                "source": "Wikipedia",
            })

    # Search the full claim text
    try:
        for title in wikipedia.search(claim, results=3)[:3]:
            try:
                add_page(wiki_api.page(title))
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
    except Exception:
        pass

    # Per-entity direct search
    try:
        doc = nlp(claim)
        entities = [
            e.text for e in doc.ents
            if e.label_ not in ["CARDINAL", "ORDINAL", "DATE", "TIME"]
        ]
        if not entities:
            entities = [
                c.text for c in doc.noun_chunks
                if not c.text.strip().isdigit()
            ]
        for kw in entities[:3]:
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


# ── 4. DuckDuckGo ─────────────────────────────────────────────────────
def search_duckduckgo(claim: str) -> list[dict]:
    """
    Web search via DuckDuckGo. Readability filter in the success path —
    garbled JS-rendered snippets are dropped before NLI sees them.
    """
    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(claim + " fact", max_results=5))
        return [
            {"text": h.get("body", ""), "url": h.get("href", ""), "source": "Web"}
            for h in hits
            if h.get("body") and is_readable(h.get("body", ""))
        ]
    except Exception:
        return []


# ── 5. MiniLM retrieval ranker ────────────────────────────────────────
def retrieve_top_evidence(claim: str, evidence_list: list[dict], top_k: int = 8) -> list[dict]:
    """
    MiniLM ranks evidence snippets by topical relevance and returns top_k.
    Role: retrieval only — does NOT determine the verdict.
    Source weight applied here only so short Google FC snippets are not
    ranked below longer Wikipedia pages on cosine similarity alone.
    """
    if not evidence_list:
        return []
    texts = [e["text"] for e in evidence_list if e.get("text")]
    if not texts:
        return []

    claim_vec     = embed_model.encode([claim])
    evidence_vecs = embed_model.encode(texts)
    sims          = cosine_similarity(claim_vec, evidence_vecs)[0]

    ranked = sorted(
        zip(sims.tolist(), evidence_list),
        key=lambda x: x[0] * SOURCE_WEIGHTS.get(x[1].get("source", "Web"), 0.7),
        reverse=True,
    )

    # Drop completely unrelated evidence
    ranked = [(s, e) for s, e in ranked if s > 0.15]

    return [e for _, e in ranked[:top_k]]


# ── 6. Softmax ────────────────────────────────────────────────────────
def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)


# ── 7. NLI contextual scoring ─────────────────────────────────────────
def score_with_nli(claim: str, evidence_list: list[dict]) -> list[dict]:
    """
    NLI reads each (claim, evidence) pair and outputs probabilities for
    entailment / contradiction / neutral. Purely contextual — similarity
    plays no role here. Source weight amplifies authoritative sources.
    """
    if not evidence_list:
        return []
    pairs = [(claim, extract_best_sentence(e["text"], claim)) for e in evidence_list if e.get("text")]
    if not pairs:
        return []

    raw_logits = nli_model.predict(pairs)
    if raw_logits.ndim == 1:
        raw_logits = raw_logits.reshape(1, -1)

    probs = softmax(raw_logits)

    scored = []
    for i, e in enumerate(evidence_list):
        if not e.get("text"):
            continue
        weight = get_source_weight(e.get("source", "Web"), claim)
        scored.append({
            **e,
            "entail_prob":     float(probs[i, LABEL_ENTAILMENT]),
            "contra_prob":     float(probs[i, LABEL_CONTRADICTION]),
            "neutral_prob":    float(probs[i, LABEL_NEUTRAL]),
            "entail_weighted": float(probs[i, LABEL_ENTAILMENT])    * weight,
            "contra_weighted": float(probs[i, LABEL_CONTRADICTION]) * weight,
        })
    return scored


# ── 8. Verdict ────────────────────────────────────────────────────────
def decide_verdict(nli_scored: list[dict]) -> tuple[str, float, list]:
    """
    Decides verdict based purely on NLI contextual scores.

    Gate: if not a single evidence piece has entail OR contra > 0.20,
    evidence is entirely neutral/irrelevant → Unverified immediately.

    Otherwise: combined = 60% max + 40% mean across all snippets.
    Whichever of entail / contra is higher wins, subject to needing
    either a decent absolute score (>0.30) OR a clear gap (>0.10).
    """
    if not nli_scored:
        return "Unverified", 0.0, []

    entail_w = [e["entail_weighted"] for e in nli_scored]
    contra_w = [e["contra_weighted"] for e in nli_scored]

    combined_entail = 0.6 * max(entail_w) + 0.4 * float(np.mean(entail_w))
    combined_contra = 0.6 * max(contra_w) + 0.4 * float(np.mean(contra_w))

    best_entail_raw = max(e["entail_prob"] for e in nli_scored)
    best_contra_raw = max(e["contra_prob"] for e in nli_scored)

    if best_entail_raw < 0.20 and best_contra_raw < 0.20:
        return "Unverified", 0.0, []

    gap = abs(combined_entail - combined_contra)

    if combined_entail >= combined_contra:
        if combined_entail > 0.30 or gap > 0.10:
            verdict, confidence = "True", combined_entail
        else:
            verdict, confidence = "Unverified", combined_entail
    else:
        if combined_contra > 0.30 or gap > 0.10:
            verdict, confidence = "False", combined_contra
        else:
            verdict, confidence = "Unverified", combined_contra

    top_two = sorted(nli_scored, key=lambda e: e["entail_weighted"], reverse=True)[:2]
    clean_evidence = [
        {"text": e["text"], "url": e["url"], "source": e["source"]}
        for e in top_two
    ]

    return verdict, round(confidence, 3), clean_evidence


# ── Main entry point ──────────────────────────────────────────────────
def verify_claims(claims: list[str]) -> list[dict]:
    """
    Verifies a list of claims and returns results.

    Filtering and capping are handled UPSTREAM — no duplication here:
      - services/claim_extractor.py  → is_worth_verifying() filters vague sentences
      - routes/verify.py             → MAX_CLAIMS = 10 cap per request

    This function trusts that the list it receives is already clean.
    """
    results = []

    for claim in claims:
        # Step 1: Build focused search queries from the claim's own context
        smart_queries = build_smart_queries(claim)

        # Step 2: Gather evidence — Google FC + Wikipedia REST + fallback + DDG
        # Only keep GFC results that are actually about this claim
        # (GFC returns results for similar-sounding claims, not exact matches)
        raw_google = search_google_factcheck(claim)
        if raw_google:
            claim_vec = embed_model.encode([claim])
            gfc_vecs  = embed_model.encode([e["text"] for e in raw_google])
            gfc_sims  = cosine_similarity(claim_vec, gfc_vecs)[0]
            google_evidence = [
                e for e, s in zip(raw_google, gfc_sims) if s > 0.40
            ]
        else:
            google_evidence = []
        
        rest_evidence   = search_wikipedia_rest(smart_queries)   # primary
        wiki_evidence   = search_wikipedia_fallback(claim)       # safety net
        ddg_evidence    = search_duckduckgo(claim)

        all_evidence = google_evidence + rest_evidence + wiki_evidence + ddg_evidence

        # Step 3: MiniLM ranks by topical relevance — retrieval only
        top_evidence = retrieve_top_evidence(claim, all_evidence, top_k=8)
        if not top_evidence:
            top_evidence = all_evidence[:8]

        # Step 4: NLI reads claim + evidence contextually — verdict only
        nli_scored = score_with_nli(claim, top_evidence)

        # Step 5: Decide verdict from NLI scores alone
        verdict, confidence, used_evidence = decide_verdict(nli_scored)

        results.append({
            "claim":      claim,
            "verdict":    verdict,
            "confidence": round(confidence, 3),
            "similarity": round(confidence, 3),
            "evidence":   used_evidence,
        })

    return results