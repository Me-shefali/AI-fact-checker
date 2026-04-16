# 🔍 AI-Fact-Checker
 
**AI-Fact-Checker** is a web-based application that verifies factual information from text, documents, and article URLs. It uses NLP techniques to extract claims, compare them with trusted sources, and generate confidence-based, explainable verification results through a React frontend and Python (FastAPI) backend.
 
> 📚 *Academic Project*  
> 👩‍💻 *Shefali Chouhan & Garima Choudhary*
 
---
 
## 📌 Table of Contents
 
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [How It Works](#how-it-works)
- [Expected Outcomes](#expected-outcomes)
---
 
## Overview
 
Misinformation has become a critical concern in modern society, influencing public opinion, education, and decision-making. Most existing fact-checking tools operate as black-box systems, offering no transparency or explanation for their verdicts.
 
**AI-Fact-Checker** addresses this by providing:
- Claim-wise, explainable verification results
- Confidence scores and reference links
- Support for multiple input formats (text, PDF/DOCX, URLs)
- An assistant that supports — not replaces — human judgment
---
 
## Features
 
- 📝 **Text Input** — Paste any text directly for fact-checking
- 📄 **Document Upload** — Upload PDF or DOCX files for claim extraction
- 🔗 **URL Analysis** — Submit article URLs for automated scraping and verification
- 🧠 **NLP Claim Extraction** — Identifies factual, verifiable claims from input content
- ✅ **Verdict Labels** — Each claim is labeled as *Supported*, *Partially Supported*, or *Not Supported*
- 📊 **Confidence Scores** — Each verdict comes with a confidence percentage
- 🔎 **Source References** — Trusted reference links are provided for each claim
- 💡 **Explainable AI** — Results are transparent, not black-box
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Python, FastAPI |
| NLP | spaCy, NLTK |
| Semantic Similarity | Sentence Transformers, scikit-learn |
| Document Parsing | PyPDF2, python-docx |
| Web Scraping | Newspaper3k, BeautifulSoup |
| API Communication | Axios / Fetch API |
| Data Validation | Pydantic |
| Server | Uvicorn |
| Database *(optional)* | SQLite / PostgreSQL |
 
---

 
## Getting Started
 
### Prerequisites
 
- Node.js & npm
- Python 3.8+
- pip
### 1. Clone the Repository
 
```bash
git clone https://github.com/Me-shefali/AI-fact-checker.git
cd AI-fact-checker
```
 
### 2. Setup Backend
 
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
 
The FastAPI server will start at `http://localhost:8000`.  
Auto-generated API docs available at `http://localhost:8000/docs`.
 
### 3. Setup Frontend
 
```bash
cd frontend
npm install
npm start
```
 
The React app will start at `http://localhost:3000`.
 
---

## How It Works
 
```
User Input (Text / Document / URL)
        ↓
  Content Extraction
  (text parsing, web scraping)
        ↓
  Text Preprocessing
  (cleaning, tokenization, sentence splitting)
        ↓
  Claim Identification
  (spaCy NLP — filters factual sentences from opinions)
        ↓
  Evidence Retrieval
  (trusted public knowledge sources)
        ↓
  Fact Verification
  (Sentence Transformers + cosine similarity)
        ↓
  Result Generation
  (verdict + confidence score + reference links)
        ↓
  Displayed in React UI
```
 
---

## Expected Outcomes
 
- ✅ A functional web-based AI-assisted fact-checking system
- ✅ Claim-wise verification results with confidence scores and supporting references
- ✅ Improved transparency and explainability in automated fact-checking
- ✅ Reduced manual effort required to verify information
- ✅ Increased awareness and responsible consumption of online information
- 
---
 
This project is developed for academic purposes.
 
