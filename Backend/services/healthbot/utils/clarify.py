def build_clarification(nlp_data):
    if not nlp_data.get("symptoms"):
        return {
            "type": "clarification",
            "message": "Can you describe your symptoms in a bit more detail?"
        }

    if nlp_data.get("intent") == "general_question":
        return {
            "type": "clarification",
            "message": "Are you asking for general information, or are you experiencing symptoms?"
        }

    return {
        "type": "clarification",
        "message": "Could you provide a little more information so I can help you better?"
    }
