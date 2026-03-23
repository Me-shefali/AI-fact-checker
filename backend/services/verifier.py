# verifier.py
import httpx
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()

import wikipediaapi
from duckduckgo_search import DDGS
from sentence_transformers import CrossEncoder

# Load NLI model once at startup (replaces cosine similarity)
nli_model = CrossEncoder("cross-encoder/nli-deberta-v3-base")
#LABEL_MAP = ["contradiction", "entailment", "neutral"]

GOOGLE_FC_API_KEY = os.getenv("GOOGLE_FC_API_KEY")


# ── 1. Google Fact Check ──────────────────────────────────────────────
def search_google_factcheck(claim: str) -> list[dict]:
    """Returns list of {text, url, source} from professional fact-checkers."""
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": claim, "key": GOOGLE_FC_API_KEY, "languageCode": "en"}
    try:
        r = httpx.get(url, params=params, timeout=8)
        data = r.json()
        results = []
        for item in data.get("claims", [])[:3]:
            for review in item.get("claimReview", []):
                results.append({
                    "text": f"{item.get('text','')} — Rating: {review.get('textualRating','')}",
                    "url": review.get("url", ""),
                    "source": review.get("publisher", {}).get("name", "Google Fact Check")
                })
        return results
    except Exception:
        return []


# ── 2. Wikipedia summary ─────────────────────────────────────────────
def search_wikipedia(claim: str) -> list[dict]:
    """Extract named entities from claim and fetch Wikipedia summaries."""
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(claim)
    results = []
    wiki = wikipediaapi.Wikipedia(user_agent="FactChecker/1.0", language="en")
    for ent in doc.ents[:2]:  # top 2 entities only
        page = wiki.page(ent.text)
        if page.exists():
            results.append({
                "text": page.summary[:500],
                "url": page.fullurl,
                "source": "Wikipedia"
            })
            # Fallback: search Wikipedia directly with the claim
    if not results:
        try:
            search_results = wiki.search(claim, results=2)
            for title in search_results[:2]:
                page = wiki.page(title)
                if page.exists():
                    results.append({
                        "text": page.summary[:500],
                        "url": page.fullurl,
                        "source": "Wikipedia"
                    })
        except Exception:
            pass

    return results


# ── 3. DuckDuckGo web search ──────────────────────────────────────────
def search_duckduckgo(claim: str) -> list[dict]:
    """Free web search fallback, no API key needed."""
    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(claim, max_results=3))
        return [
            {"text": h.get("body", ""), "url": h.get("href", ""), "source": "Web"}
            for h in hits if h.get("body")
        ]
    except Exception:
        return []
    
def softmax(x):
    # Convert raw NLI logits to proper 0.0–1.0 probabilities
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)


# ── 4. NLI verdict ────────────────────────────────────────────────────
def classify_with_nli(claim: str, evidence_list: list[dict]) -> tuple[str, float, list]:
    """
    Run NLI cross-encoder on each evidence snippet.
    Returns verdict, confidence, and top evidence used.
    """
    if not evidence_list:
        return "Unverified", 0.0, []

    pairs = [(claim, e["text"]) for e in evidence_list if e.get("text")]
    if not pairs:
        return "Unverified", 0.0, []

    raw_scores = nli_model.predict(pairs)

    # Apply softmax — fixes the 441% / 3.11% bug
    if raw_scores.ndim == 1:
        raw_scores = raw_scores.reshape(1, -1)
    scores = softmax(raw_scores)  # now properly 0.0–1.0

    best_entailment = float(max(scores[:, 1]))   # column 1 = entailment
    best_contradiction = float(max(scores[:, 0])) # column 0 = contradiction

    if best_entailment > 0.7:
        verdict, confidence = "True", float(best_entailment)
    elif best_contradiction > 0.7:
        verdict, confidence = "False", float(best_contradiction)
    else:
        verdict, confidence = "Unverified", max(best_entailment, best_contradiction)

    # Return top 2 evidence snippets
    top_evidence = sorted(
        zip(scores[:, 1].tolist(), evidence_list),
        reverse=True
    )[:2]
    used_evidence = [e for _, e in top_evidence]

    return verdict, round(confidence,3), used_evidence


# ── Main entry point ──────────────────────────────────────────────────
def verify_claims(claims: list[str]) -> list[dict]:
    results = []

    for claim in claims:
        # Priority chain: Google FC → Wikipedia → DDG
        evidence = search_google_factcheck(claim)

        if len(evidence) < 2:
            evidence += search_wikipedia(claim)

        if len(evidence) < 2:
            evidence += search_duckduckgo(claim)

        verdict, confidence, used_evidence = classify_with_nli(claim, evidence)

        results.append({
            "claim": claim,
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "similarity": round(confidence, 3),  # keep for DB compatibility
            "evidence": used_evidence
        })

    return results