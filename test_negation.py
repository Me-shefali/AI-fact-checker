import sys
sys.path.insert(0, 'backend')

from services.verifier import verify_claim

print("=" * 60)
print("Test 1: False negated claim")
print("=" * 60)
result = verify_claim('New Delhi is not the capital of India.')
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Expected: Likely False")
print()

print("=" * 60)
print("Test 2: Negated true claim (Chinese universities)")
print("=" * 60)
result = verify_claim('Chinese Universities did not rise in the list of top 100 across the world.')
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Note: Should show high contradiction if universities DID rise")
