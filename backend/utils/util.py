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
    set1 = set(extract_key_terms(claim1))
    set2 = set(extract_key_terms(claim2))

    if not set1 or not set2:
        return 0.0

    # Jaccard similarity on key terms
    jaccard = len(set1 & set2) / len(set1 | set2) if len(set1 | set2) > 0 else 0

    # Phrase match bonus - check if claim appears in text or vice versa
    phrase_bonus = 0.1 if (
        claim1[:80].lower() in claim2.lower() or 
        claim2[:80].lower() in claim1.lower() or
        claim1.lower() in claim2.lower() or
        claim2.lower() in claim1.lower()
    ) else 0

    # Key term presence - bonus if ANY of the important terms appear in the text
    important_terms = set1  # terms from the claim
    term_presence = len(important_terms & set2) / len(important_terms) if important_terms else 0
    term_presence_bonus = min(term_presence * 0.15, 0.15)  # up to 15% bonus

    # Number matching bonus
    nums1 = set(re.findall(r"\d+", claim1))
    nums2 = set(re.findall(r"\d+", claim2))
    number_bonus = 0.1 if nums1 & nums2 else 0

    # Calculate final similarity as weighted combination
    final_similarity = (
        jaccard * 0.4 +           # 40% weight on exact term overlap
        phrase_bonus +             # 10% if phrase appears
        term_presence_bonus +      # up to 15% if key terms present
        number_bonus               # 10% if numbers match
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


def detect_negation(text: str) -> bool:
    """Detect if a claim contains negation (not, no, never, etc.)"""
    negation_patterns = [
        r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bneither\b',
        r'\bno.*?able\b', r'\bcan\'?t\b', r'\bwouldn\'?t\b',
        r'\bdon\'?t\b', r'\bdoesn\'?t\b', r'\bdidn\'?t\b',
        r'\bisn\'?t\b', r'\baren\'?t\b', r'\bwasn\'?t\b', r'\bweren\'?t\b'
    ]
    text_lower = text.lower()
    for pattern in negation_patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def remove_negation(text: str) -> str:
    """Remove negation from a claim for NLI comparison"""
    negation_removals = [
        (r'\bis\s+not\b', 'is'),
        (r'\bare\s+not\b', 'are'),
        (r'\bwas\s+not\b', 'was'),
        (r'\bwere\s+not\b', 'were'),
        (r'\bnot\s+', ''),
        (r'\bno\s+', ''),
        (r'\bn\'?t\b', ''),
    ]
    result = text
    for pattern, replacement in negation_removals:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result.strip()


def assess_support_direction(claim: str, text: str) -> Dict[str, Any]:
    try:
        # 🔴 Check if claim contains negation
        has_negation = detect_negation(claim)
        claim_for_nli = remove_negation(claim) if has_negation else claim

        # Use NLI model on the non-negated claim
        scores = nli_model.predict([(claim_for_nli, text)])[0]  # [contradiction, entailment, neutral]
        contradiction_score = scores[0]
        entailment_score = scores[1]
        neutral_score = scores[2]

        # Determine direction based on highest score
        if entailment_score > contradiction_score and entailment_score > neutral_score:
            direction = "support"
            confidence_delta = float(entailment_score) * 0.1
        elif contradiction_score > entailment_score and contradiction_score > neutral_score:
            direction = "contradict"
            confidence_delta = float(contradiction_score) * 0.1
        else:
            direction = "neutral"
            confidence_delta = 0.0

        # 🔴 FLIP DIRECTION IF ORIGINAL CLAIM WAS NEGATED
        if has_negation:
            if direction == "support":
                direction = "contradict"
                confidence_delta = float(entailment_score) * 0.1  # Scale based on how well evidence supports the negated claim
            elif direction == "contradict":
                direction = "support"
                confidence_delta = float(contradiction_score) * 0.1

        support_count = float(entailment_score)
        contradict_count = float(contradiction_score)

    except Exception as e:
        print(f"[NLI] Error in NLI prediction: {str(e)[:100]}")
        # Fallback to keyword-based with negation handling
        has_negation = detect_negation(claim)
        lower_text = text.lower()
        support_count = sum(1 for marker in SUPPORTIVE_MARKERS if marker in lower_text)
        contradict_count = sum(1 for marker in CONTRADICTORY_MARKERS if marker in lower_text)

        if support_count and contradict_count:
            direction = "neutral"
        elif contradict_count:
            direction = "contradict"
        elif support_count:
            direction = "support"
        else:
            direction = "neutral"

        # 🔴 FLIP DIRECTION IF CLAIM HAD NEGATION
        if has_negation and direction != "neutral":
            direction = "contradict" if direction == "support" else "support"

        confidence_delta = 0.0
        if direction == "support":
            confidence_delta = 0.06
        elif direction == "contradict":
            confidence_delta = -0.08

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