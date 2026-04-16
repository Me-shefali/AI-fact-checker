from services.verifier import search_evidence, score_evidence
from utils.util import calculate_claim_similarity

claim = 'New Delhi is the capital of India.'
queries = ['New Delhi is the capital of India.', 'New Delhi capital India']

evidence = search_evidence(queries)
print('evidence count', len(evidence))
for i, e in enumerate(evidence, 1):
    print(i, e.get('url'), e.get('domain'), 'len', len(e.get('text', '')))
    print('sim', calculate_claim_similarity(claim, e.get('text', '')))

scored = score_evidence(claim, evidence)
print('scored count', len(scored))
for i, s in enumerate(scored, 1):
    print(i, s.get('domain'), s.get('relevance'), s.get('support_direction'), s.get('confidence'))
