from typing import List, Dict
from ddgs import DDGS
from newspaper import Article

from services.config import *
from utils.util import *

# ── SCRAPE HELPER ───────────────────────────────────────
def scrape_full_text(url: str) -> str:
    """Scrapes full text from a URL using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[SCRAPE] Failed to scrape {url}: {str(e)[:50]}")
        return ""

# ── BUILD TRUSTED SEARCH FILTER ─────────────────────────
def build_trusted_filter():
    return "(" + " OR ".join([f"site:{d}" for d in TRUSTED_DOMAINS]) + ")"

# ── SEARCH FUNCTION ─────────────────────────────────────
def search_evidence(queries: List[str], max_results: int = 5) -> List[Dict]:
    results = []
    seen_urls = set()
    
    # 1. Broad Search (Always run first to get diverse sources)
    print(f"[SEARCH] Running broad search for {len(queries)} queries...")
    with DDGS() as ddgs:
        for q_idx, q in enumerate(queries):
            print(f"[SEARCH] Query {q_idx}: {q[:60]}...")
            try:
                # Run broad search
                for r in ddgs.text(q, max_results=MAX_SEARCH_RESULTS):
                    url = r.get("href", "")
                    if not url or url in seen_urls:
                        continue
                    
                    # Filter out obvious non-news/boilerplate URLs
                    if any(x in url.lower() for x in ["facebook.com", "twitter.com", "instagram.com", "youtube.com/watch?v="]):
                        continue

                    seen_urls.add(url)
                    results.append({
                        "title": r.get("title", ""),
                        "text": " ".join(filter(None, [
                            r.get("snippet", ""),
                            r.get("title", "")
                        ])),
                        "url": url,
                        "domain": extract_domain(url)
                    })
            except Exception as e:
                print(f"[SEARCH] Query {q_idx} failed: {str(e)[:100]}")
                continue

    # 2. Targeted Search for Trusted Sources (Boosting)
    # We already have results, but we might want to ensure we didn't miss trusted ones
    trusted_filter = build_trusted_filter()
    print(f"[SEARCH] Running targeted trusted search...")
    try:
        with DDGS() as ddgs:
            # Just run the most important query with trusted filter
            for r in ddgs.text(f"{queries[0]} {trusted_filter}", max_results=3):
                url = r.get("href", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                results.append({
                    "title": r.get("title", ""),
                    "text": r.get("snippet", ""),
                    "url": url,
                    "domain": extract_domain(url)
                })
    except:
        pass

    # 🚀 ENHANCEMENT: Scrape top 3 results for richer context (increased from 2)
    # We sort by snippet relevance briefly to pick which to scrape
    temp_scored = []
    for r in results:
        # Simple word match for priority scraping
        score = sum(1 for word in queries[0].lower().split() if word in r["text"].lower())
        temp_scored.append((score, r))
    
    temp_scored.sort(key=lambda x: x[0], reverse=True)
    results_to_scrape = [x[1] for x in temp_scored[:3]]

    print(f"[SEARCH] Scraping top {len(results_to_scrape)} results for deeper context...")
    for r in results_to_scrape:
        full_text = scrape_full_text(r["url"])
        if full_text and len(full_text) > 200:
            # Clean boilerplate from full text
            full_text = re.sub(r"Add .* as your preferred source.*", "", full_text, flags=re.IGNORECASE)
            full_text = re.sub(r"Click here to .*|Read more.*", "", full_text, flags=re.IGNORECASE)
            r["text"] = full_text[:3500] 

    final_count = len(results)
    print(f"[SEARCH] FINAL: {final_count} results before truncation to {max_results}")
    return results[:max_results]


# ── SCORE EACH EVIDENCE ─────────────────────────────────
def score_evidence(claim: str, evidence_list: List[Dict]) -> List[Dict]:
    scored = []
    print(f"[SCORE] Starting with {len(evidence_list)} evidence items")

    for idx, e in enumerate(evidence_list):
        text = e.get("text", "").strip()
        url = e.get("url", "")

        # 🔥 FILTER BOILERPLATE
        if "as your preferred source" in text.lower() or "subscribe to" in text.lower():
            print(f"[SCORE] Item {idx}: SKIPPED - boilerplate detected")
            continue

        if not text or len(text) < 50: # Increased min length for better quality
            print(f"[SCORE] Item {idx}: SKIPPED - text too short ({len(text)} chars)")
            continue

        print(f"[SCORE] Item {idx}: text='{text[:200]}...'")
        similarity = calculate_claim_similarity(claim, text)
        print(f"[SCORE] Item {idx}: similarity={similarity:.3f}, threshold={SIMILARITY_THRESHOLD}")

        if similarity < SIMILARITY_THRESHOLD:
            print(f"[SCORE] Item {idx}: FILTERED - similarity {similarity:.3f} < {SIMILARITY_THRESHOLD}")
            continue

        domain = e.get("domain") or extract_domain(url)
        credibility = calculate_source_credibility(domain, text)

        # Domain matching - if claim mentions the domain/agency, boost credibility
        if any(term in claim.lower() for term in domain.split('.')):
            credibility = min(credibility + 0.15, 0.98)
            print(f"[SCORE] Item {idx}: Topic-relevant domain boost applied")

        trusted = (
            domain in TRUSTED_DOMAINS or
            domain.endswith(".gov") or
            domain.endswith(".int") or
            domain.endswith(".edu") or
            domain.endswith(".gov.in")
        )

        reliability_bonus = 0.0
        if trusted:
            reliability_bonus = 0.12 # Increased bonus
            credibility = min(credibility + 0.1, 0.98)

        direction = assess_support_direction(claim, text)

        # Adjusted scoring weights for better accuracy
        final_score = min(
            WEIGHT_SIMILARITY * similarity +
            WEIGHT_CREDIBILITY * credibility +
            WEIGHT_RELIABILITY * reliability_bonus +
            WEIGHT_DIRECTION * direction["confidence_delta"],
            1.0
        )

        print(f"[SCORE] Item {idx}: ACCEPTED - score={final_score:.3f}, direction={direction['direction']}")

        scored.append({
            "text": text,
            "url": url,
            "domain": domain,
            "source": domain,
            "trusted_source": trusted,
            "similarity": round(similarity, 3),
            "confidence": round(credibility, 3),
            "support_direction": direction["direction"],
            "relevance": round(final_score, 3)
        })

    print(f"[SCORE] Final: {len(scored)} evidence items passed")
    return sorted(scored, key=lambda x: x["relevance"], reverse=True)


# ── FINAL VERDICT LOGIC ─────────────────────────────────
def aggregate_verdict(scored_evidence: List[Dict]) -> Dict:
    print(f"[VERDICT] Aggregating {len(scored_evidence)} scored evidence items")
    
    if not scored_evidence:
        print("[VERDICT] NO EVIDENCE - returning default Unverified")
        return {
            "verdict": "Unverified",
            "confidence": 0.2,
            "reason": "No reliable evidence found"
        }

    all_scores = [e["relevance"] for e in scored_evidence]
    max_score = max(all_scores)
    avg_score = sum(all_scores) / len(all_scores)
    trusted_count = sum(1 for e in scored_evidence if e.get("trusted_source"))
    trusted_ratio = trusted_count / len(scored_evidence)
    support_sum = sum(e["relevance"] for e in scored_evidence if e.get("support_direction") == "support")
    contradict_sum = sum(e["relevance"] for e in scored_evidence if e.get("support_direction") == "contradict")
    sample_size_bonus = min(len(all_scores) / 5, VERDICT_SAMPLE_BONUS)

    print(f"[VERDICT] max={max_score:.3f}, avg={avg_score:.3f}, support={support_sum:.3f}, contradict={contradict_sum:.3f}, trusted_ratio={trusted_ratio:.3f}")

    direction_delta = min(max((support_sum - contradict_sum) / max(sum(all_scores), 1), -0.15), 0.15)
    final_score = (
        VERDICT_TRUE_POSITIVE_WEIGHT * max_score +
        VERDICT_TRUE_NEGATIVE_WEIGHT * avg_score +
        VERDICT_TRUST_WEIGHT * trusted_ratio +
        sample_size_bonus +
        direction_delta
    )
    final_score = min(max(final_score, 0.0), 1.0)
    print(f"[VERDICT] final_score={final_score:.3f}")

    # 🔴 FIX #3: Better verdict logic that handles all cases
    # Priority 1: Check strong contradiction (and no support)
    if contradict_sum > support_sum and contradict_sum > 0.2:
        # Strong contradiction found
        verdict = "Likely False"
    # Priority 2: Check strong support  
    elif support_sum > contradict_sum and support_sum > 0.2:
        # Clear support found
        verdict = "Likely True"
    # Priority 3: Check final score for high confidence
    elif final_score >= VERDICT_LIKELY_TRUE_THRESHOLD:
        # High score with no strong contradiction
        verdict = "Likely True"
    # Priority 4: Check for unverified threshold
    elif final_score >= VERDICT_UNVERIFIED_MIN:
        # Medium confidence, mixed evidence
        verdict = "Unverified"
    # Default: Low confidence
    else:
        verdict = "Likely False"

    print(f"[VERDICT] FINAL: {verdict} (confidence={final_score:.3f})")
    return {
        "verdict": verdict,
        "confidence": round(final_score, 3),
    }


# ── MAIN VERIFY FUNCTION ────────────────────────────────
def verify_claim(claim: str) -> Dict:
    print(f"\n{'='*60}")
    print(f"[VERIFY] Processing claim: {claim[:80]}...")
    print(f"{'='*60}\n")
    
    # ── SAFETY CHECK ──
    safety = check_content_safety(claim)

    # ── QUICK FAKE CHECK ──
    fake_check = detect_obvious_fake_patterns(claim)

    # ── MANIPULATION ANALYSIS ──
    manipulation = detect_manipulation_patterns(claim)

    # ── TEMPORAL ANALYSIS ───────────────────────────────
    temporal = extract_temporal_indicators(claim)

    # ── GENERATE SEARCH QUERIES ──────────────────────────
    queries = generate_search_queries(claim)
    print(f"[VERIFY] Generated {len(queries)} search queries: {queries}\n")

    # ── FETCH EVIDENCE ─────────────────────────────────
    evidence = search_evidence(queries)
    print(f"[VERIFY] Retrieved {len(evidence)} evidence items\n")

    # ── SCORE EVIDENCE ─────────────────────────────────
    scored = score_evidence(claim, evidence)
    print(f"[VERIFY] Scored {len(scored)} evidence items\n")

    # ── AGGREGATE RESULT ─────────────────────────────
    verdict_data = aggregate_verdict(scored)

    # ── EVIDENCE SUMMARY ─────────────────────────────
    summary = summarize_evidence_quality(scored)

    return {
        "claim": claim,
        "verdict": verdict_data["verdict"],
        "confidence": verdict_data["confidence"],
        "evidence": scored[:5],
        "summary": summary,
        "manipulation": manipulation,
        "fake_pattern": fake_check,
        "temporal": temporal,
        "safety": safety,
        "queries_used": queries,
    }