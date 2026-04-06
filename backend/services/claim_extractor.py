from services.nlp_model import nlp

def is_worth_verifying(sentence: str) -> bool:
    """
    Skip claims that are too vague, too short, or purely subjective
    to be fact-checkable against external sources.
    """
    doc = nlp(sentence)
    
    # Too short to be meaningful
    if len(doc) < 5:
        return False
    
    # Must have at least one named entity OR a number
    # (vague claims like "it is important" have neither)
    has_entity = any(ent.label_ in ["GPE","ORG","PERSON","NORP",
                                     "DATE","CARDINAL","QUANTITY"] 
                     for ent in doc.ents)
    has_number = any(token.like_num for token in doc)
    
    if not has_entity and not has_number:
        return False
    
    return True

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
            if is_worth_verifying(sentence):  # ADD THIS CHECK
                claims.append(sentence)

        elif has_verb and len(doc) >= 3:
            # FIX: was >= 4, dropped short facts like "Earth orbits Sun."
            # (3 tokens). Lowered to >= 3.
            if is_worth_verifying(sentence):
                claims.append(sentence)

        elif has_subject and len(doc) >= 3:
            # FIX: accept subject-only sentences — handles copular facts like
            # "New Delhi is the capital of India" where spaCy's small model
            # sometimes tags "is" as AUX rather than VERB.
            if is_worth_verifying(sentence):
                claims.append(sentence)

    return claims