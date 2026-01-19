from utils.rules_loader import load_emergencies 

EMERGENCIES = load_emergencies()

def detect_intent(text: str):
    for emergency in EMERGENCIES:
        if emergency in text:
            return "emergency"

        if any(word in text for word in ["have", "having", "suffering", "feeling"]):
               return "symptom_check" 

        if text.endswith("?"):
               return "general_question" 

        return "unknown"
