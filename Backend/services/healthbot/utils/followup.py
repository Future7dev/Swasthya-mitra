from utils.database import get_conversation_history, get_session as db_get_session
import json
import time

FOLLOWUP_KEYWORDS = {
    "symptom_check": [
        "How are you feeling now?",
        "Have your symptoms improved?",
        "Is the pain still present?",
        "Did the treatment help?",
        "Any new symptoms?",
    ],
    "medication": [
        "Are you taking the medication regularly?",
        "Any side effects from the medicine?",
        "Did you get the prescription?",
        "Need help with dosage?",
    ],
    "appointment": [
        "Did you schedule the appointment?",
        "How was your visit to the doctor?",
        "Did you follow up with your doctor?",
    ],
    "general_question": [
        "Do you have any other questions?",
        "Is there anything else you'd like to know?",
        "Can I help with anything else?",
    ],
}

def get_last_intent(session_id: str) -> str:
    history = get_conversation_history(session_id, limit=10)
    for msg in reversed(history):
        if msg["role"] == "assistant":
            content = msg.get("content", "")
            if "risk" in content.lower():
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
    
    if current_intent:
        intent = current_intent
    elif last_intent:
        intent = last_intent
    else:
        intent = get_last_intent(session_id)
    
    if intent in FOLLOWUP_KEYWORDS:
        return FOLLOWUP_KEYWORDS[intent][0]
    
    if last_symptoms:
        return "How are those symptoms feeling now?"
    
    return "Is there anything else I can help you with?"

def get_session_summary(session_id: str) -> dict:
    history = get_conversation_history(session_id, limit=50)
    session = db_get_session(session_id)
    
    symptoms_mentioned = []
    intents = []
    
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"].lower()
            if "symptom" in content or "pain" in content or "feeling" in content:
                symptoms_mentioned.append(msg["content"][:50])
        elif msg["role"] == "assistant":
            if "risk" in msg.get("content", "").lower():
                intents.append("symptom_check")
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "last_symptoms": symptoms_mentioned[-5:] if symptoms_mentioned else [],
        "intents": intents[-5:] if intents else [],
        "last_active": session.get("last_active_at") if session else None
    }

def check_previous_context(session_id: str, current_input: str) -> dict:
    current_lower = current_input.lower()
    history = get_conversation_history(session_id, limit=10)
    
    reference_keywords = ["that", "those", "it", "they", "them", "previous", "earlier", "before", "last time"]
    
    if any(kw in current_lower for kw in reference_keywords) and history:
        return {
            "has_reference": True,
            "recent_context": history[-3:] if len(history) >= 3 else history
        }
    
    return {"has_reference": False}