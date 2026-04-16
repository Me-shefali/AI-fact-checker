from services.nlp_model import nlp
import re
from datetime import datetime
from nltk.corpus import wordnet

def is_readable(text: str) -> bool:
    if not text or len(text) < 30:
        return False

    words = text.split()
    if not words:
        return False

    long_words = sum(1 for w in words if len(w) > 20)
    return (long_words / len(words)) < 0.30


def extract_temporal_indicators(text: str):
    current_year = datetime.now().year

    return {
        "has_recent_indicators": any(
            word in text.lower()
            for word in ["current", "latest", "recent", "now", "today"]
        ),
        "year": current_year
    }


def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)[:2]


def build_smart_queries(claim: str):
    doc = nlp(claim)

    weighted_queries = []

    # 🔴 1. EXACT MATCH (highest priority)
    weighted_queries.append((claim, 1.1))

    # 🔴 2. NAMED ENTITIES
    named_entities = [
        ent.text for ent in doc.ents
        if ent.label_ in ["GPE", "ORG", "PERSON", "NORP", "FAC", "LOC", "PRODUCT"]
    ]

    if len(named_entities) >= 2:
        weighted_queries.append((" ".join(named_entities[:2]), 1.0))
        weighted_queries.append((f"{named_entities[0]} {named_entities[1]}", 0.95))

    elif len(named_entities) == 1:
        weighted_queries.append((named_entities[0], 0.9))

    # 🔴 3. DEPENDENCY-BASED QUERY (VERY IMPORTANT)
    for token in doc:
        if token.dep_ in ("ROOT", "attr", "dobj"):
            subject = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            obj = [w.text for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]

            if subject and obj:
                dep_query = f"{subject[0]} {token.lemma_} {obj[0]}"
                weighted_queries.append((dep_query, 1.0))

    # 🔴 4. NOUN CHUNKS (fallback - skip synonyms as they cause word-sense confusion)
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    if noun_chunks:
        weighted_queries.append((" ".join(noun_chunks[:2]), 0.75))

    # 🔴 6. REMOVE DUPLICATES + SORT
    seen = set()
    final_queries = []

    for q, w in sorted(weighted_queries, key=lambda x: x[1], reverse=True):
        if q not in seen:
            seen.add(q)
            final_queries.append(q)

    # Filter out single-word queries
    final_queries = [q for q in final_queries if len(q.split()) >= 2]

    return final_queries[:5]