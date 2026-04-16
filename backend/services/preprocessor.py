import re
import unicodedata
from services.nlp_model import nlp

def clean_text(text: str) -> str:
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    return text


def preprocess_text(raw_text):
    if not raw_text or not raw_text.strip():
        return []

    text = clean_text(raw_text)

    # Preserve punctuation important for NER
    text = re.sub(r"[^a-zA-Z0-9\s\.\!\?\,\'\-\"]", "", text)

    text = re.sub(r'\s+', ' ', text).strip()

    doc = nlp(text)

    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    return sentences