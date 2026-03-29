import random

def build_clarification(nlp_data, state):
    last_question = state.get("last_question")
    symptoms_mentioned = nlp_data.get("symptoms", [])
    intent = nlp_data.get("intent", "")
    severity = nlp_data.get("severity", "unknown")
    
    if not symptoms_mentioned:
        state["last_question"] = "symptoms"
        
        clarification_options = [
            "Can you tell me more about what you're experiencing? For example, do you have pain, fever, cough, or any other symptoms?",
            "I'd like to help you better. Could you describe what you're feeling or any symptoms you have?",
            "What symptoms are you experiencing? Try to describe how you feel physically.",
            "To help you properly, please share what you're feeling - any pain, discomfort, or unusual sensations?",
            "Could you tell me more about what you're going through? Any physical symptoms you'd like to describe?"
        ]
        
        if intent == "emergency":
            clarification_options.insert(0, "This sounds serious. Can you describe your symptoms immediately so I can help?")
        
        return {
            "type": "clarification",
            "message": random.choice(clarification_options)
        }
    
    duration = nlp_data.get("duration")
    if duration is None and last_question != "duration":
        state["last_question"] = "duration"
        
        duration_options = [
            "How long have you been experiencing these symptoms? Is it a few hours, days, or longer?",
            "When did these symptoms start? Have they been going on for a while?",
            "How long have you been feeling this way? Is it recent or has it been ongoing?",
            "Do you know how long you've had these symptoms? Days, weeks, or just started?",
            "Since when have you been experiencing this? Has it been getting worse?"
        ]
        
        return {
            "type": "clarification",
            "message": random.choice(duration_options)
        }
    
    severity_val = nlp_data.get("severity", "unknown")
    if severity_val == "unknown" and last_question != "severity":
        state["last_question"] = "severity"
        
        severity_options = [
            "How severe is this? Is it mild, moderate, or severe?",
            "On a scale, how bad is it? Are you able to function normally?",
            "Is the pain or discomfort intense, or is it manageable?",
            "Would you describe this as mild, moderate, or severe?",
            "How would you rate the severity - is it影响到 your daily activities?"
        ]
        
        return {
            "type": "clarification",
            "message": random.choice(severity_options)
        }
    
    if intent in ["medical_advice", "general_question"] and last_question != "advice":
        state["last_question"] = "advice"
        
        advice_options = [
            "Is there something specific you'd like to know about your condition?",
            "What specific information would help you?",
            "Do you have any particular concerns about your health right now?",
            "What would you like me to help you with specifically?"
        ]
        
        return {
            "type": "clarification",
            "message": random.choice(advice_options)
        }
    
    state["last_question"] = "general"
    general_options = [
        "Could you provide any additional details that might help me understand better?",
        "Is there anything else you'd like to share about how you're feeling?",
        "Any other information that might be helpful for me to know?",
        "Do you have any other symptoms or concerns you'd like to mention?"
    ]
    
    return {
        "type": "clarification",
        "message": random.choice(general_options)
    }
