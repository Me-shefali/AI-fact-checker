import re
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def preprocess_text(raw_text):

    if not raw_text or not raw_text.strip():
        return []

    # Convert to lowercase
    text = raw_text.lower()

    # Remove unwanted symbols but keep sentence punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\.\!\?]', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Sentence splitting using spaCy
    doc = nlp(text)

    # Return cleaned sentences
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    return sentences