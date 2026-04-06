from services.nlp_model import nlp

def is_readable(text: str) -> bool:
    """
    Reject garbled DDG snippets from JS-rendered pages.
    If >30% of words are >20 chars it's likely concatenated junk text.
    """
    if not text or len(text) < 30:
        return False
    words = text.split()
    if not words:
        return False
    long_words = sum(1 for w in words if len(w) > 20)
    return (long_words / len(words)) < 0.30


# ── Helper: build search queries from the claim ───────────────────────
def build_smart_queries(claim: str) -> list[str]:
    """
    Build focused Wikipedia/web search queries using the claim's own
    context — no hardcoded word dictionary needed.

    Logic:
    - 2+ named entities → search their combination
        "Tehran is the capital of Iran" → ["Tehran Iran", "Tehran and Iran"]
    - 1 named entity + content words → entity + context disambiguates
        "Apple is a fruit"             → ["Apple fruit"]
        "Python is used for data science" → ["Python data science"]
    - No named entities → use content words directly
        "There are 7 continents"       → ["continents world"]

    The claim itself always carries the disambiguation signal — we never
    need to hard-code what "apple" or "python" means.
    """
    doc = nlp(claim)

    named_entities = [
        ent.text for ent in doc.ents
        if ent.label_ in ["GPE", "ORG", "PERSON", "NORP", "FAC", "LOC", "PRODUCT"]
    ]

    entity_texts_lower = {e.lower() for e in named_entities}

    # Content words: nouns, adjectives, non-stop verbs — excluding the
    # entity words already captured above
    content_words = [
        token.text for token in doc
        if token.pos_ in ["NOUN", "ADJ", "VERB"]
        and not token.is_stop
        and token.text.lower() not in entity_texts_lower
        and len(token.text) > 2
    ]

    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    queries = []

    # Case 1: two or more named entities
    if len(named_entities) >= 2:
        queries.append(" ".join(named_entities[:2]))
        queries.append(f"{named_entities[0]} and {named_entities[1]}")

    # Case 2: exactly one named entity — append content words to disambiguate
    elif len(named_entities) == 1:
        entity = named_entities[0]
        context = " ".join(content_words[:2])
        queries.append(f"{entity} {context}".strip() if context else entity)

    # Case 3: no named entities — content words are the query
    else:
        if content_words:
            queries.append(" ".join(content_words[:3]))
        if noun_chunks:
            queries.append(" ".join(c.split()[0] for c in noun_chunks[:3]))

    # Always add noun-chunk fallback
    if noun_chunks:
        queries.append(" ".join(noun_chunks[:2]))

    # Deduplicate preserving order
    seen, unique = set(), []
    for q in queries:
        q = q.strip()
        if q and q not in seen:
            seen.add(q)
            unique.append(q)

    return unique[:4]
