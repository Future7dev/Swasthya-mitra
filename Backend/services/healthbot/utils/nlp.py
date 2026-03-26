import re
from utils.rules_loader import load_symptoms, load_emergencies

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except:
    nlp = None
    HAS_SPACY = False

SYMPTOM_RULES = load_symptoms()
EMERGENCIES = load_emergencies()

NEGATIONS = {"not", "no", "dont", "don't", "doesnt", "doesn't", "without", "never", "neither", "nor", "none", "nothing", "neither"}

URGENCY_WORDS = {
    "high": {"severe", "intense", "extreme", "critical", "urgent", "emergency", "worsening", "sudden"},
    "medium": {"moderate", "concerning", "worrying", "persistent", "recurring"},
    "low": {"mild", "slight", "minor", "occasional", "sometimes"}
}

INTENT_PATTERNS = {
    "emergency": ["emergency", "urgent", "critical", "dying", "unconscious", "bleeding", "chest pain", "can't breathe", "can't breath"],
    "symptom_check": ["i have", "i'm feeling", "i feel", "having", "suffering", "experiencing", "my", "pain", "hurt", "ache", "sick"],
    "medical_advice": ["should i", "what should", "do i need", "can i", "is it normal", "help", "advice", "recommend"],
    "follow_up": ["follow up", "check up", "after that", "previous", "earlier", "before", "what did", "remember"],
    "general_question": ["what is", "how does", "why", "when", "where", "who", "explain"],
    "medication": ["medicine", "medication", "drug", "pill", "tablet", "dose", "prescription", "take", "prescribe"],
    "appointment": ["appointment", "schedule", "doctor", "visit", "clinic", "hospital", "see a doctor"],
}

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str):
    text = normalize(text)
    return text.split()

def extract_symptoms(text: str):
    found = set()
    text_lower = text.lower()
    tokens = set(tokenize(text))
    
    for symptom, data in SYMPTOM_RULES.items():
        if symptom in text_lower:
            if not _is_negated(symptom, text_lower):
                found.add(symptom)
        for alias in data.get("aliases", []):
            if alias in text_lower and not _is_negated(alias, text_lower):
                found.add(symptom)
        for keyword in data.get("keywords", []):
            if keyword in tokens:
                found.add(symptom)

    return list(found)

def _is_negated(term: str, text: str) -> bool:
    words = text.split()
    for i, word in enumerate(words):
        if term in word or word == term:
            start = max(0, i - 3)
            window = words[start:i]
            if any(neg in " ".join(window) for neg in NEGATIONS):
                return True
    return False

def extract_duration(text: str):
    text_lower = text.lower()
    
    patterns = [
        (r"(\d+)\s*(day|days)", 86400),
        (r"(\d+)\s*(week|weeks)", 604800),
        (r"(\d+)\s*(month|months)", 2592000),
        (r"(\d+)\s*(hour|hours)", 3600),
        (r"since\s+(\d+)\s*(day|days|week|weeks|month|months)", 86400),
    ]
    
    for pattern, _ in patterns:
        match = re.search(pattern, text_lower)
        if match:
            num = int(match.group(1))
            if "week" in match.group(0):
                return num * 7
            if "month" in match.group(0):
                return num * 30
            if "hour" in match.group(0):
                return num / 24
            return num
    
    if "today" in text_lower or "since this morning" in text_lower:
        return 1
    if "yesterday" in text_lower:
        return 2
    if "few days" in text_lower or "couple of days" in text_lower:
        return 3
    if "week" in text_lower:
        return 7
    if "long time" in text_lower or "while" in text_lower:
        return 14
    
    return None

def extract_severity(text: str) -> str:
    text_lower = text.lower()
    
    for level, words in URGENCY_WORDS.items():
        if any(word in text_lower for word in words):
            return level
    
    if "worse" in text_lower or "worsening" in text_lower:
        return "high"
    if "better" in text_lower or "improving" in text_lower:
        return "low"
    
    return "unknown"

def extract_urgency(text: str) -> str:
    text_lower = text.lower()
    
    if any(word in text_lower for word in URGENCY_WORDS["high"]):
        return "high"
    if any(word in text_lower for word in URGENCY_WORDS["medium"]):
        return "medium"
    return "low"

def detect_intent(text: str) -> str:
    text_lower = normalize(text)
    scores = {}
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if pattern in text_lower:
                score += 1
        scores[intent] = score
    
    for emergency in EMERGENCIES:
        if emergency in text_lower:
            return "emergency"
    
    max_score = max(scores.values())
    if max_score > 0:
        for intent, score in scores.items():
            if score == max_score:
                return intent
    
    return "unknown"

def extract_medical_entities(text: str) -> dict:
    entities = {
        "body_parts": [],
        "conditions": [],
        "measurements": []
    }
    
    text_lower = text.lower()
    
    body_parts = ["head", "chest", "stomach", "back", "leg", "arm", "hand", "foot", "face", "eye", "ear", "nose", "throat"]
    for part in body_parts:
        if part in text_lower:
            entities["body_parts"].append(part)
    
    conditions = ["fever", "cough", "cold", "flu", "infection", "allergy", "diabetes", "blood pressure"]
    for cond in conditions:
        if cond in text_lower:
            entities["conditions"].append(cond)
    
    return entities

def analyze_text(raw_text: str) -> dict:
    text = normalize(raw_text)
    tokens = tokenize(text)
    
    return {
        "intent": detect_intent(text),
        "symptoms": extract_symptoms(raw_text),
        "duration": extract_duration(raw_text),
        "severity": extract_severity(raw_text),
        "urgency": extract_urgency(raw_text),
        "entities": extract_medical_entities(raw_text),
        "tokens": tokens,
        "original": raw_text
    }