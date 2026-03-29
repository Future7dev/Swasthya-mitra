def build_response(nlp_data, rules, emergencies):
    if nlp_data.get("intent") == "emergency":
        return {
            "risk": "EMERGENCY",
            "message": "This sounds like it could be a medical emergency. Please seek immediate medical attention by calling emergency services or going to your nearest emergency room right away.",
            "action": "emergency"
        }

    symptoms = nlp_data.get("symptoms", [])
    duration = nlp_data.get("duration")
    severity = nlp_data.get("severity", "unknown")
    urgency = nlp_data.get("urgency", "low")

    if not symptoms:
        return {
            "risk": "UNKNOWN",
            "message": "I couldn't identify specific symptoms from your message. Please describe what you're experiencing in more detail.",
            "action": "clarify"
        }

    responses = []
    escalate = False
    risk_level = "LOW"
    recognized_symptoms = []
    unrecognized_symptoms = []

    for s in symptoms:
        rule = rules.get(s)
        if rule:
            recognized_symptoms.append(s)
            responses.append(f"For {s}: {rule['advice']}")
            
            if rule.get("severity") == "high" or rule.get("severity") == "medium":
                if risk_level == "LOW":
                    risk_level = rule["severity"].upper()
            
            if duration is not None and rule.get("doctor_after_days", 7):
                if duration >= rule["doctor_after_days"]:
                    escalate = True
        else:
            unrecognized_symptoms.append(s)

    if not recognized_symptoms:
        return {
            "risk": "UNKNOWN",
            "message": f"You mentioned: {', '.join(symptoms)}. I don't have specific information about this in my database. Please consult a healthcare professional for proper evaluation.",
            "action": "doctor_recommendation",
            "symptoms_not_found": symptoms
        }

    if severity == "high" or urgency == "high":
        risk_level = "HIGH"
        escalate = True

    if escalate:
        if risk_level == "LOW":
            risk_level = "MEDIUM"
        responses.append("Based on your symptoms, I recommend consulting a healthcare provider soon.")

    response_message = " ".join(responses)
    
    if unrecognized_symptoms:
        response_message += f"\n\nNote: I don't have specific information about '{', '.join(unrecognized_symptoms)}' in my database."

    if duration is not None:
        if duration <= 1:
            response_message += " Since your symptoms just started, monitor them closely."
        elif duration >= 7:
            response_message += " Since your symptoms have persisted for a while, please consider seeing a doctor."

    return {
        "risk": risk_level,
        "message": response_message,
        "action": "advice",
        "recognized_symptoms": recognized_symptoms,
        "unrecognized_symptoms": unrecognized_symptoms
    }
