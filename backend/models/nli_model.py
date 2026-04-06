from sentence_transformers import CrossEncoder

print("Loading NLI model...")

nli_model = CrossEncoder("MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

print("NLI model loaded successfully.")