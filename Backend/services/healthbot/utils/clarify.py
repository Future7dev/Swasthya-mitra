def build_clarification(nlp_data, state):
    if not state.get("symptoms"):
        state["last_question"] = "symptoms"
        return {
            "type": "clarification",
            "message": "Can you describe your symptoms in more detail?"
        }

    if not state.get("duration"):
        state["last_question"] = "duration"
        return {
            "type": "clarification",
            "message": "How long have you been experiencing these symptoms?"
        }

    return {
        "type": "clarification",
        "message": "Could you provide a bit more information?"
    }

