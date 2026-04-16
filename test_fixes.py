#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from services.claim_extractor import extract_claims
from services.preprocessor import preprocess_text
from services.verifier import verify_claim
from utils.util import detect_negation
from services.nlp_model import nlp

print("=" * 70)
print("FIX #1: CLAIM EXTRACTION - Now accepting claims with 'revolve'")
print("=" * 70)

test_texts = [
    "The Earth does not revolve around the Sun.",
    "The Sun revolves around the Earth.",
    "The Earth revolves around the Moon.",
]

for text in test_texts:
    sentences = preprocess_text(text)
    claims = extract_claims(sentences)
    print(f"\nInput: {text}")
    print(f"Extracted claims: {claims}")
    print(f"✓ FIXED!" if claims else "✗ STILL BROKEN")

print("\n" + "=" * 70)
print("FIX #2: META-CLAIM DETECTION - Filtering belief statements")
print("=" * 70)

from services.claim_extractor import is_meta_claim

meta_test_cases = [
    ("Studies show that the Earth is round.", True),
    ("The Earth is round.", False),
    ("Researchers believe the Sun is at the center.", True),
    ("The Sun is at the center.", False),
    ("People think cats can fly.", True),
    ("Cats can fly.", False),
]

for text, should_be_meta in meta_test_cases:
    result = is_meta_claim(text)
    status = "✓" if result == should_be_meta else "✗"
    print(f"{status} '{text}' → Meta-claim: {result} (expected {should_be_meta})")

print("\n" + "=" * 70)
print("FIX #3: NEGATION HANDLING - Testing verdict flipping")
print("=" * 70)

negation_tests = [
    ("The Earth does not revolve around the Moon.", False, "Likely False"),
    ("The Earth revolves around the Sun.", True, "Likely True"),
    ("It is not true that the Earth is not round.", True, "Likely True"),
]

for claim, is_true, expected_verdict in negation_tests:
    print(f"\n{'-' * 70}")
    print(f"Testing claim: {claim}")
    print(f"Expected result: {expected_verdict}")
    
    has_neg = detect_negation(claim)
    print(f"Has negation: {has_neg}")
    
    result = verify_claim(claim)
    print(f"Got verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.3f}")
    
    match = result['verdict'] == expected_verdict
    print(f"Result: {'✓ CORRECT' if match else '✗ MISMATCH'}")
