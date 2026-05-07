import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse

from services.config import *
from models.nli_model import nli_model
from utils.helper import is_readable, build_smart_queries  # ✅ integrate helper


# ── TEXT CLEANING ───────────────────────────────────────
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)

    return text


# ── VALIDATION ──────────────────────────────────────────
def validate_input_text(text: str):
    if not text:
        return False, "Text required"

    text = text.strip()

    if len(text) < MIN_TEXT_LENGTH:
        return False, "Text too short"

    if len(text) > MAX_TEXT_LENGTH:
        return False, "Text too long"

    if not is_readable(text):  # ✅ NEW
        return False, "Text not readable / noisy"

    return True, None


def validate_url(url: str):
    if not url:
        return False, "URL required"

    if len(url) > MAX_URL_LENGTH:
        return False, "URL too long"

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False, "Invalid URL"

    return True, None


# ── LANGUAGE CHECK ──────────────────────────────────────
def detect_english_confidence(text: str) -> float:
    ascii_chars = len(re.findall(r"[A-Za-z]", text))
    total = len(text)

    if total == 0:
        return 0.0

    return round(ascii_chars / total, 3)


def is_english_text(text: str, minimum_confidence: float = 0.65) -> bool:
    if not text or len(text) < 20:
        return False

    confidence = detect_english_confidence(text)
    return confidence >= minimum_confidence


# ── KEY TERM EXTRACTION ─────────────────────────────────
def extract_key_terms(text: str, max_terms=10) -> List[str]:
    words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", text.lower())

    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    return sorted(freq, key=freq.get, reverse=True)[:max_terms]


# ── SMART QUERY BUILDER (NEW) ───────────────────────────
def generate_search_queries(claim: str) -> List[str]:
    """
    Uses NLP-based query builder from helper.py
    """
    try:
        return build_smart_queries(claim)
    except Exception:
        return [claim]  # fallback


# ── DOMAIN EXTRACTION (NEW) ─────────────────────────────
def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "").lower()
    except:
        return "unknown"


# ── SIMILARITY ──────────────────────────────────────────
def calculate_claim_similarity(claim1: str, claim2: str) -> float:
    # 1. Keyword Overlap (Jaccard)
    set1 = set(extract_key_terms(claim1))
    set2 = set(extract_key_terms(claim2))

    if not set1 or not set2:
        return 0.0

    jaccard = len(set1 & set2) / len(set1 | set2) if len(set1 | set2) > 0 else 0

    # 2. Fuzzy Phrase Matching
    # Check for significant overlapping sequences
    c1_low = claim1.lower()
    c2_low = claim2.lower()
    
    # Split into smaller chunks to find matches
    chunks = [c1_low[i:i+30] for i in range(0, min(len(c1_low), 150), 20)]
    chunk_matches = sum(1 for chunk in chunks if len(chunk) > 10 and chunk in c2_low)
    phrase_match_score = min(chunk_matches / max(len(chunks), 1), 0.25)

    # 3. Direct Key Entity Check
    entities1 = set(re.findall(r"\b[A-Z][a-z]+\b", claim1))
    entities2 = set(re.findall(r"\b[A-Z][a-z]+\b", claim2))
    entity_overlap = len(entities1 & entities2) / len(entities1) if entities1 else 0
    entity_bonus = min(entity_overlap * 0.2, 0.2)

    # 4. Number matching bonus
    nums1 = set(re.findall(r"\d+", claim1))
    nums2 = set(re.findall(r"\d+", claim2))
    number_match = len(nums1 & nums2) / len(nums1) if nums1 else 0
    number_bonus = min(number_match * 0.15, 0.15)

    # Calculate final similarity
    final_similarity = (
        jaccard * 0.4 +           # 40% weight on exact term overlap
        phrase_match_score +       # up to 25% for partial phrase matches
        entity_bonus +             # up to 20% if key entities match
        number_bonus               # up to 15% if numbers match
    )

    return min(final_similarity, 1.0)


# ── CREDIBILITY ─────────────────────────────────────────
def calculate_source_credibility(domain: str, claim_text: str = "") -> float:
    domain = domain.lower()

    base = SOURCE_CREDIBILITY_SCORES.get(domain, SOURCE_CREDIBILITY_SCORES["unknown"])
    claim_lower = claim_text.lower()

    bonus = 0
    for topic, domains in DOMAIN_EXPERTISE_BONUS.items():
        if any(d in domain for d in domains):
            if topic in claim_lower:
                bonus = 0.05
                break

    source_bonus = 0
    if domain.endswith(".gov") or domain.endswith(".int") or domain.endswith(".edu") or domain.endswith(".gov.in"):
        source_bonus = 0.05

    regional_bonus = 0
    if any(marker in claim_lower for marker in CULTURAL_PATTERNS.get("regional_markers", [])):
        if domain.endswith(".in") or domain.endswith(".gov.in") or domain in {
            "factchecker.in", "boomlive.in", "altnews.in", "pib.gov.in"
        }:
            regional_bonus = 0.04

    return min(base + bonus + source_bonus + regional_bonus, 0.98)


SUPPORTIVE_MARKERS = [
    "confirmed", "reported", "stated", "found", "verified", "according to",
    "says", "announced", "declared", "acknowledged"
]
CONTRADICTORY_MARKERS = [
    "debunked", "false", "not true", "no evidence", "myth", "incorrect",
    "proved wrong", "refuted", "denied", "unsubstantiated"
]


def detect_negation_count(text: str) -> int:
    """Detect number of negation markers in a text to handle double negations."""
    negation_patterns = [
        r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bneither\b',
        r'\bno.*?able\b', r'\bcan\'?t\b', r'\bwouldn\'?t\b',
        r'\bdon\'?t\b', r'\bdoesn\'?t\b', r'\bdidn\'?t\b',
        r'\bisn\'?t\b', r'\baren\'?t\b', r'\bwasn\'?t\b', r'\bweren\'?t\b',
        r'\bfalse\b', r'\buntrue\b', r'\bincorrect\b', r'\bdeny\b', r'\bdenies\b'
    ]
    text_lower = text.lower()
    count = 0
    for pattern in negation_patterns:
        count += len(re.findall(pattern, text_lower))
    return count


def remove_negations(text: str) -> str:
    """Carefully remove negation markers for NLI comparison."""
    negation_removals = [
        (r'\bis\s+not\b', 'is'),
        (r'\bare\s+not\b', 'are'),
        (r'\bwas\s+not\b', 'was'),
        (r'\bwere\s+not\b', 'were'),
        (r'\bnot\b', ''),
        (r'\bno\b', ''),
        (r'\bn\'t\b', ''),
        (r'\bfalse\b', ''),
        (r'\buntrue\b', ''),
    ]
    result = text
    for pattern, replacement in negation_removals:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Clean up double spaces
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def assess_support_direction(claim: str, text: str) -> Dict[str, Any]:
    try:
        # 🔴 Handle complex negations
        claim_neg_count = detect_negation_count(claim)
        text_neg_count = detect_negation_count(text)
        
        # We compare non-negated versions for NLI base similarity
        clean_claim = remove_negations(claim)
        clean_text = remove_negations(text)

        print(f"[NLI] Original Claim: {claim} (Negs: {claim_neg_count})")
        print(f"[NLI] Original Text: {text[:100]}... (Negs: {text_neg_count})")

        # Use NLI model
        scores = nli_model.predict([(claim, text)])[0]  # [contradiction, entailment, neutral]
        contradiction_score = scores[0]
        entailment_score = scores[1]
        neutral_score = scores[2]

        print(f"[NLI] Raw Scores - Entailment: {entailment_score:.3f}, Contradiction: {contradiction_score:.3f}")

        # Determine raw direction
        if entailment_score > contradiction_score and entailment_score > 0.3:
            direction = "support"
            confidence_delta = float(entailment_score) * 0.12
        elif contradiction_score > entailment_score and contradiction_score > 0.3:
            direction = "contradict"
            confidence_delta = float(contradiction_score) * 0.12
        else:
            # If model is uncertain, try the "clean" versions
            clean_scores = nli_model.predict([(clean_claim, clean_text)])[0]
            if clean_scores[1] > clean_scores[0] and clean_scores[1] > 0.4:
                # They are about the same topic, so use negation parity to decide
                parity = (claim_neg_count % 2) == (text_neg_count % 2)
                direction = "support" if parity else "contradict"
                confidence_delta = float(clean_scores[1]) * 0.08
                print(f"[NLI] Parity check used: direction={direction}")
            else:
                direction = "neutral"
                confidence_delta = 0.0

        print(f"[NLI] Final direction: {direction}")

        support_count = float(entailment_score)
        contradict_count = float(contradiction_score)

    except Exception as e:
        print(f"[NLI] Error: {str(e)}")
        direction = "neutral"
        confidence_delta = 0.0
        support_count = 0.5
        contradict_count = 0.5

    return {
        "direction": direction,
        "confidence_delta": confidence_delta,
        "support_count": support_count,
        "contradict_count": contradict_count
    }


# ── MANIPULATION DETECTION ─────────────────────────────
def detect_manipulation_patterns(text: str) -> Dict:
    text = text.lower()

    result = {
        "patterns": {},
        "score": 0
    }

    total_score = 0

    for category, words in MANIPULATION_INDICATORS.items():
        found = [w for w in words if w in text]

        if found:
            result["patterns"][category] = found
            total_score += len(found) * 15

    result["score"] = min(total_score, 100)

    return result


# ── FAKE PATTERN QUICK CHECK ───────────────────────────
def detect_obvious_fake_patterns(text: str) -> Dict:
    text = text.lower()
    confidence = 0
    flags = []

    if any(x in text for x in ["forward this", "share with everyone"]):
        confidence += 40
        flags.append("viral_forward")

    if "miracle cure" in text:
        confidence += 50
        flags.append("too_good_to_be_true")

    if "breaking" in text and "official" not in text:
        confidence += 20
        flags.append("unverified_breaking")

    return {
        "is_fake": confidence >= 60,
        "confidence": min(confidence, 95),
        "flags": flags
    }


# ── TEMPORAL ANALYSIS ──────────────────────────────────
def extract_temporal_indicators(text: str) -> Dict:
    current_year = datetime.utcnow().year

    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text)

    return {
        "years": years,
        "mentions_current_year": str(current_year) in text,
        "is_recent": any(x in text.lower() for x in ["today", "breaking", "now"]),
    }


# ── EVIDENCE QUALITY ───────────────────────────────────
def summarize_evidence_quality(results: List[Dict]) -> Dict:
    if not results:
        return {
            "total": 0,
            "avg_relevance": 0,
            "avg_credibility": 0
        }

    total_rel = 0
    total_cred = 0

    for r in results:
        total_rel += float(r.get("relevance", 0))
        total_cred += float(r.get("confidence", 0))

    return {
        "total": len(results),
        "avg_relevance": round(total_rel / len(results), 3),
        "avg_credibility": round(total_cred / len(results), 3),
    }


# ── SAFETY ─────────────────────────────────────────────
def check_content_safety(text: str) -> Dict:
    text = text.lower()

    flags = []

    for category, patterns in HARMFUL_CONTENT_PATTERNS.items():
        for p in patterns:
            if p in text:
                flags.append(category)

    if not flags:
        return {"safe": True}

    return {
        "safe": False,
        "flags": list(set(flags)),
        "risk": "high" if "violence" in flags else "medium"
    }