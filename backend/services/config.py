import os

# ── APP SETTINGS ─────────────────────────────────────────
APP_NAME = "AI Fact Checker"

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en"}

# ── INPUT LIMITS ─────────────────────────────────────────
MAX_TEXT_LENGTH = 8000
MIN_TEXT_LENGTH = 20   # increased slightly (better quality)
MAX_URL_LENGTH = 2048
MAX_FILE_SIZE = 25 * 1024 * 1024

MAX_EXTRACTED_TEXT_LENGTH = 20000
MAX_ANALYSIS_TEXT_LENGTH = 5000

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# ── MODEL CONFIG ─────────────────────────────────────────
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
#GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ── SEARCH CONFIG ────────────────────────────────────────
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID", "")
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

MAX_SEARCH_RESULTS = 10
TRUSTED_RESULTS_RATIO = 0.7   # Prefer trusted sources while still allowing broader retrieval

# ── VERIFICATION THRESHOLDS ─────────────────────────────
SIMILARITY_THRESHOLD = 0.10
HIGH_CONFIDENCE_THRESHOLD = 0.70
MIN_EVIDENCE_REQUIRED = 2

# ── SCORING WEIGHTS ─────────────────────────────────────
WEIGHT_SIMILARITY = 0.55
WEIGHT_CREDIBILITY = 0.30
WEIGHT_RELIABILITY = 1.00
WEIGHT_DIRECTION = 1.00

# ── VERDICT AGGREGATION ─────────────────────────────────
VERDICT_TRUE_POSITIVE_WEIGHT = 0.50
VERDICT_TRUE_NEGATIVE_WEIGHT = 0.30
VERDICT_TRUST_WEIGHT = 0.12
VERDICT_SAMPLE_BONUS = 0.08
VERDICT_LIKELY_TRUE_THRESHOLD = 0.62
VERDICT_UNVERIFIED_MIN = 0.38
VERDICT_LIKELY_FALSE_THRESHOLD = 0.32

# ── SOURCE CREDIBILITY ───────────────────────────────────
SOURCE_CREDIBILITY_SCORES = {
    "pib.gov.in": 0.95,
    "reuters.com": 0.92,
    "apnews.com": 0.91,
    "ap.org": 0.91,
    "bbc.com": 0.90,
    "factcheck.org": 0.89,
    "factchecker.in": 0.88,
    "boomlive.in": 0.85,
    "altnews.in": 0.85,
    "thehindu.com": 0.83,
    "indianexpress.com": 0.82,
    "hindustantimes.com": 0.80,
    "snopes.com": 0.88,
    "politifact.com": 0.88,
    "theguardian.com": 0.84,
    "nytimes.com": 0.84,
    "cnn.com": 0.75,
    "ndtv.com": 0.75,
    "wikipedia.org": 0.70,
    "timesofindia.indiatimes.com": 0.68,
    "youtube.com": 0.50,
    "twitter.com": 0.45,
    "facebook.com": 0.40,
    "reddit.com": 0.55,
    "unknown": 0.50,
}

# 🔥 NEW: TRUSTED DOMAINS FOR SEARCH FILTERING
TRUSTED_DOMAINS = [
    "reuters.com", "apnews.com", "bbc.com",
    "factcheck.org", "snopes.com", "politifact.com",
    "pib.gov.in", "factchecker.in", "boomlive.in",
    "altnews.in", "thehindu.com", "indianexpress.com",
    "hindustantimes.com"
]

# ── DOMAIN EXPERTISE ─────────────────────────────────────
DOMAIN_EXPERTISE_BONUS = {
    "health": ["who.int", "cdc.gov", "mohfw.gov.in", "icmr.gov.in"],
    "science": ["nature.com", "science.org", "isro.gov.in", "csir.res.in"],
    "finance": ["imf.org", "worldbank.org", "rbi.org.in", "finmin.nic.in"],
    "technology": ["openai.com", "nist.gov", "cert-in.org.in", "meity.gov.in"],
}

CULTURAL_PATTERNS = {
    "festivals": [
        "diwali", "deepavali", "holi", "eid", "christmas", "dussehra",
        "vijaya dashami", "navratri", "ganesh chaturthi", "karva chauth",
        "raksha bandhan", "rakhi", "janmashtami", "durga puja",
        "kali puja", "onam", "pongal", "makar sankranti",
        "baisakhi", "gudi padwa", "ugadi", "poila boishakh",
        "vishu", "bihu"
    ],
    "government_schemes": [
        "pm kisan", "pradhan mantri kisan", "ayushman bharat",
        "jan aushadhi", "pradhan mantri", "swachh bharat",
        "digital india", "make in india", "skill india",
        "startup india", "beti bachao", "ujjwala yojana",
        "jal jeevan mission", "atmanirbhar bharat", "mudra loan",
        "jan dhan"
    ],
    "political_terms": [
        "bjp", "congress", "aap", "aam aadmi party", "election",
        "parliament", "lok sabha", "rajya sabha", "chief minister",
        "cm", "prime minister", "pm", "modi", "rahul gandhi",
        "kejriwal", "election commission", "evm"
    ],
    "health_terms": [
        "ayurveda", "homeopathy", "covid", "coronavirus", "vaccine",
        "vaccination", "covishield", "covaxin", "immunity",
        "kadha", "tulsi", "turmeric", "haldi"
    ],
    "regional_markers": [
        "punjab", "haryana", "rajasthan", "gujarat", "maharashtra",
        "karnataka", "kerala", "tamil nadu", "andhra pradesh",
        "telangana", "west bengal", "bihar", "uttar pradesh",
        "delhi", "mumbai", "kolkata", "chennai"
    ]
}

# ── MANIPULATION DETECTION ──────────────────────────────
MANIPULATION_INDICATORS = {
    "emotional_triggers": ["shocking", "unbelievable", "terrifying"],
    "urgency_tactics": ["urgent", "act now", "breaking"],
    "authority_claims": ["experts say", "study shows"],
    "social_proof": ["everyone is saying", "going viral"],
    "fear_appeals": ["deadly", "dangerous", "crisis"],
}

# ── SAFETY FILTER ───────────────────────────────────────
HARMFUL_CONTENT_PATTERNS = {
    "violence": ["kill", "bomb", "attack"],
    "hate_speech": ["racial hatred", "ethnic cleansing"],
    "self_harm": ["suicide", "self harm"],
}