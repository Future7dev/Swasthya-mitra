from utils.database import get_conversation_history, get_session as db_get_session
import json
import random

FOLLOWUP_KEYWORDS = {
    "symptom_check": [
        "How are you feeling now? Have your symptoms improved or gotten worse?",
        "Is the pain or discomfort still there? Any changes?",
        "Are you feeling any better since we last talked?",
        "Any updates on how you're feeling?",
        "Have your symptoms changed at all since our last conversation?"
    ],
    "medication": [
        "Are you taking any medications as recommended? Any side effects?",
        "Did you manage to get the prescription? How are you responding to it?",
        "Have you started any new medication? How is it working?",
        "Any concerns about your current medications?",
        "Are the medications helping with your symptoms?"
    ],
    "appointment": [
        "Were you able to schedule an appointment with a doctor?",
        "How did your doctor's appointment go?",
        "Did you get a chance to see a healthcare professional?",
        "Have you followed up with your doctor as recommended?",
        "Any updates from your medical appointment?"
    ],
    "emergency": [
        "I hope you're safe now. Are you receiving the help you need?",
        "Please let me know if you need any additional information.",
        "Are you in a safe location and receiving medical care?"
    ],
    "general_question": [
        "Do you have any other health questions I can help with?",
        "Is there anything else you'd like to know about your health?",
        "Can I help you with any other medical concerns?",
        "Any other questions about your symptoms or health?"
    ]
}

def get_last_intent(session_id: str) -> str:
    history = get_conversation_history(session_id, limit=10)
    for msg in reversed(history):
        if msg["role"] == "assistant":
            content = msg.get("content", "").lower()
            if "emergency" in content or "risk" in content:
                return "symptom_check"
    return "unknown"

def generate_followup(session_id: str, current_intent: str | None = None) -> str | None:
    session = db_get_session(session_id)
    if not session:
        return None
    
    context_json = session.get("context_json", "{}")
    try:
        context = json.loads(context_json) if context_json else {}
    except:
        context = {}
    
    last_symptoms = context.get("symptoms", [])
    last_intent = context.get("last_intent")
    last_risk = context.get("last_risk")
    
    if current_intent:
        intent = current_intent
    elif last_intent:
        intent = last_intent
    else:
        intent = get_last_intent(session_id)
    
    if last_risk == "EMERGENCY" or last_risk == "HIGH":
        return random.choice(FOLLOWUP_KEYWORDS["emergency"])
    
    if intent in FOLLOWUP_KEYWORDS:
        return random.choice(FOLLOWUP_KEYWORDS[intent])
    
    if last_symptoms:
        return random.choice(FOLLOWUP_KEYWORDS["symptom_check"])
    
    return random.choice(FOLLOWUP_KEYWORDS["general_question"])

def get_session_summary(session_id: str) -> dict:
    history = get_conversation_history(session_id, limit=50)
    session = db_get_session(session_id)
    
    symptoms_mentioned = []
    intents = []
    risks = []
    
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"].lower()
            if "symptom" in content or "pain" in content or "feeling" in content:
                symptoms_mentioned.append(msg["content"][:50])
        elif msg["role"] == "assistant":
            if "risk" in msg.get("content", "").lower():
                intents.append("symptom_check")
            if "emergency" in msg.get("content", "").lower():
                risks.append("emergency")
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "last_symptoms": symptoms_mentioned[-5:] if symptoms_mentioned else [],
        "intents": intents[-5:] if intents else [],
        "risks": risks[-5:] if risks else [],
        "last_active": session.get("last_active_at") if session else None
    }

def check_previous_context(session_id: str, current_input: str) -> dict:
    current_lower = current_input.lower()
    history = get_conversation_history(session_id, limit=10)
    
    reference_keywords = ["that", "those", "it", "they", "them", "previous", "earlier", "before", "last time", "what did you say", "repeat"]
    
    if any(kw in current_lower for kw in reference_keywords) and history:
        return {
            "has_reference": True,
            "recent_context": history[-3:] if len(history) >= 3 else history
        }
    
    return {"has_reference": False}
