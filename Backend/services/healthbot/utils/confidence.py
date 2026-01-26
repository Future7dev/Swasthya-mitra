def assess_confidence(nlp_data, rules):
    symptoms = nlp_data.get("symptoms", [])
    intent = nlp_data.get("intent")
    duration = nlp_data.get("duration")

    if intent == "emergency":
        return "high"
    
    if not symptoms:
        return "low"

    for s in symptoms:
        if s not in rules:
            return "low"

        if duration is None:
            return "low"

    if intent in ["unknown", "general_question"]:
        return "low"

    return "high"
