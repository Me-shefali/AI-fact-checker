import spacy

nlp = spacy.load("en_core_web_sm")

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
            claims.append(sentence)

    return claims