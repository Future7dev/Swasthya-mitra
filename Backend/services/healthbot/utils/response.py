def build_response(nlp_data, rules, emergencies):
    if nlp_data.get("intent") == "emergency":
        return {
            "risk": "EMERGENCY",
            "message": "This may be a medical emergency. Please seek immediate medical care immediately."
        }

    symptoms = nlp_data.get("symptoms", [])
    responses = []

    for s in symptoms:
        if s in rules:
            responses.append(rules[s]["advice"])

    if not responses:
        return {
            "risk": "UNKNOWN",
            "message": "I couldn’t identify specific symptoms. Please consult a healthcare professional."
        }

    return {
        "risk": "GENERAL",
        "message": " ".join(responses)
    }
