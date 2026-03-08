from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def verify_claims(claims):

    results = []

    for claim in claims:

        # Temporary dummy evidence
        evidence = "The Earth revolves around the Sun."

        claim_embedding = model.encode([claim])
        evidence_embedding = model.encode([evidence])

        similarity = cosine_similarity(
            claim_embedding,
            evidence_embedding
        )[0][0]

        verdict = "Unverified"

        if similarity > 0.8:
            verdict = "True"
        elif similarity < 0.4:
            verdict = "False"

        results.append({
            "claim": claim,
            "similarity": float(similarity),
            "verdict": verdict
        })

    return results