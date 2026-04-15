from services.nlp_model import nlp

SUBJECTIVE_WORDS = {"best", "worst", "amazing", "great", "bad"}

def is_worth_verifying(doc) -> bool:
    if len(doc) < 3:
        return False

    has_entity = any(ent.label_ in [
        "GPE","ORG","PERSON","DATE","CARDINAL","QUANTITY"
    ] for ent in doc.ents)

    has_number = any(token.like_num for token in doc)

    has_fact_verb = any(
        token.lemma_ in ["be", "have", "contain", "include"]
        for token in doc
    )

    if not has_entity and not has_number and not has_fact_verb:
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
                claims.append(sentence)

    return claims