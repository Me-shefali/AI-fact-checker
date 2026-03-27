from services.nlp_model import nlp

def extract_claims(sentences):
    claims = []

    for sentence in sentences:
        doc = nlp(sentence)

        has_subject = False
        has_verb = False

        for token in doc:
            if token.dep_ in ["nsubj", "nsubjpass"]:
                has_subject = True
            if token.pos_ == "VERB":
                has_verb = True

        if has_subject and has_verb:
            # Primary: proper grammatical claim
            claims.append(sentence)

        elif has_verb and len(doc) >= 3:
            # FIX: was >= 4, dropped short facts like "Earth orbits Sun."
            # (3 tokens). Lowered to >= 3.
            claims.append(sentence)

        elif has_subject and len(doc) >= 3:
            # FIX: accept subject-only sentences — handles copular facts like
            # "New Delhi is the capital of India" where spaCy's small model
            # sometimes tags "is" as AUX rather than VERB.
            claims.append(sentence)

    return claims