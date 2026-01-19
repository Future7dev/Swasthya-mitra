from fastapi import FastAPI
import json
from utils.clarify import build_clarification
from utils.confidence import assess_confidence
from utils.nlp import analyze_text
from utils.response import build_response

app = FastAPI()

with open("rules/symptoms.json") as f:
    rules = json.load(f)

with open("rules/emergencies.json") as f:
    emergencies = json.load(f)

@app.post("/chat")
def chat(message: str):
    nlp_data = analyze_text(message)

    confidence = assess_confidence(nlp_data, rules)
    
    if confidence == "low":
        return build_clarification(nlp_data)

    return build_response(nlp_data, rules, emergencies)
