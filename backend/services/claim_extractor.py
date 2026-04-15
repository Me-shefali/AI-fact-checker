from services.nlp_model import nlp
import re

SUBJECTIVE_WORDS = {"best", "worst", "amazing", "great", "bad"}
META_CLAIM_MARKERS = {
    "think", "believe", "say", "report", "claim", "argue", "suggest", "assert",
    "agree", "find", "discover", "observe", "consider", "reckon", "suppose",
    "hypothesis", "theory", "opinion", "view", "perspective", "estimate"
}


def is_meta_claim(text: str) -> bool:
    """Detect claims that are about what people believe/report, not facts themselves"""
    text_lower = text.lower()
    
    # Strong indicators that this is a meta-claim (about beliefs/reports)
    strong_patterns = [
        r"(according to|studies? show|research finds|researchers? (say|believe|claim|find))",
        r"(people|studies?|researchers?|scientists?) (think|believe|say|argue)",
    ]
    
    for pattern in strong_patterns:
        if re.search(pattern, text_lower):
            return True
    
    # Check for meta-verbs with belief framing (e.g., "I think", "It is believed")
    has_meta_verb = any(
        token.lemma_ in {"think", "believe", "suppose", "assume", "hypothesize"}
        for token in nlp(text)
    )
    
    # Only mark as meta if verb is clearly about belief/opinion
    if has_meta_verb and not any(word in text_lower for word in ["is", "are", "was", "were", "has", "have"]):
        return True
    
    return False


def is_worth_verifying(doc) -> bool:
    if len(doc) < 3:
        return False

    has_entity = any(ent.label_ in [
        "GPE","ORG","PERSON","DATE","CARDINAL","QUANTITY"
    ] for ent in doc.ents)

    has_number = any(token.like_num for token in doc)

    # 🔴 FIX #1: Accept ANY significant verb (not just be/have/contain/include)
    # This allows "revolve", "orbit", "move", "cause", etc.
    has_significant_verb = any(
        token.pos_ in ["VERB", "AUX"] and 
        token.lemma_ not in ["be", "do", "have_auxiliary"]  # filter out weak auxiliaries
        for token in doc
    )

    if not has_entity and not has_number and not has_significant_verb:
        return False

    if any(word in doc.text.lower() for word in SUBJECTIVE_WORDS):
        return False

    return True


def extract_claims(sentences):
    claims = []

    for sentence in sentences:
        doc = nlp(sentence)

        has_subject = any(token.dep_ in ["nsubj", "nsubjpass"] for token in doc)
        has_verb = any(token.pos_ in ["VERB", "AUX"] for token in doc)

        if (has_subject and has_verb) or len(doc) >= 3:
            if is_worth_verifying(doc):
                # 🔴 FIX #2: Filter out meta-claims (about beliefs, not facts)
                if not is_meta_claim(sentence):
                    claims.append(sentence)

    return claims