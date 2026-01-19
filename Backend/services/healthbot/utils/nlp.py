import re
import spacy
from spacy.matcher import PhraseMatcher
from utils.rules_loader import load_symptoms
from utils.intent import detect_intent

nlp = spacy.load("en_core_web_sm")

SYMPTOM_RULES = load_symptoms()

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for symptom, data in SYMPTOM_RULES.items():
    patterns = [nlp(symptom)]
    for alias in data.get("aliases", []):
        patterns.append(nlp(alias))
    matcher.add(symptom, patterns)

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text

def extract_symptoms(text: str):
    doc = nlp(text)
    matches = matcher(doc)

    found = set()
    for match_id, start, end in matches:
        symptom = nlp.vocab.strings[match_id]
        found.add(symptom)

    return list(found)

def extract_duration(text: str):
    match = re.search(r"(\d+)\s*(day|days)", text)
    return int(match.group(1)) if match else None

def extract_severity(text: str):
    if "mild" in text:
        return "mild"
    if "severe" in text:
        return "severe"
    return "unknown"

def analyze_text(raw_text: str):
    text = normalize(raw_text)
    return {
        "intent": detect_intent(text),
        "symptoms": extract_symptoms(text),
        "duration": extract_duration(text),
        "severity": extract_severity(text)
    }

