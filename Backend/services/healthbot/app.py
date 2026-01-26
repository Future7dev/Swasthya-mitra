from fastapi import FastAPI
import json
from utils.clarify import build_clarification
from utils.confidence import assess_confidence
from utils.nlp import analyze_text
from utils.response import build_response
from utils.session import get_session, update_session
from utils.context import merge_context

app = FastAPI()

with open("rules/symptoms.json") as f:
    rules = json.load(f)

with open("rules/emergencies.json") as f:
    emergencies = json.load(f)

@app.post("/chat")
def chat(user_input: str, session_id: str):
    session = get_session(session_id)

    new_nlp = analyze_text(user_input)
    context = merge_context(session, new_nlp)

    update_session(session_id, context)

    confidence = assess_confidence(context, rules)

    if confidence == "low":
        return build_clarification(context, session)

    return build_response(context, rules, emergencies)
