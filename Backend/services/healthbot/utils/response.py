def build_response(nlp_data, rules, emergencies):
    if nlp_data.get("intent") == "emergency":
        return {
            "risk": "EMERGENCY",
            "message": "This may be a medical emergency. Please seek immediate medical care immediately."
        }

    symptoms = nlp_data.get("symptoms", [])
    duration = nlp_data.get("duration")

    if not symptoms:
        return {
            "risk": "UNKNOWN",
            "message": "I couldn’t identify specific symptoms. Please describe what you are experiencing."
        }

    responses = []
    escalate = False

    for s in symptoms:
        rule = rules.get(s)
        if not rule:
            continue

        responses.append(rule["advice"])

        if duration is not None and duration >= rule["doctor_after_days"]:
            escalate = True

    if not responses:
        return {
            "risk": "UNKNOWN",
            "message": "I couldn’t identify specific symptoms. Please consult a healthcare professional."
        }

    if escalate:
        responses.append(
            "Since your symptoms have lasted longer than expected, please consult a doctor."
        )
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "risk": risk,
        "message": " ".join(responses)
    }

