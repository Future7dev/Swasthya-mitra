def assess_confidence(nlp_data, rules):
    symptoms = nlp_data.get("symptoms", [])
    intent = nlp_data.get("intent")
    duration = nlp_data.get("duration")
    urgency = nlp_data.get("urgency", "low")
    severity = nlp_data.get("severity", "unknown")
    
    if intent == "emergency":
        return "high"
    
    if not symptoms:
        if intent in ["medical_advice", "general_question", "follow_up", "medication", "appointment"]:
            return "medium"
        return "low"
    
    recognized_symptoms = [s for s in symptoms if s in rules]
    
    if not recognized_symptoms:
        return "medium"
    
    if urgency == "high" or severity == "high":
        return "high"
    
    if duration is None:
        if len(recognized_symptoms) >= 2:
            return "high"
        return "medium"
    
    if intent in ["symptom_check", "symptoms"]:
        return "high"
    
    if intent in ["unknown", "general_question"]:
        if len(recognized_symptoms) >= 1 and duration is not None:
            return "medium"
        return "low"
    
    return "high"
