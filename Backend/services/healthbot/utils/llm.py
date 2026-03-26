import os
import json
import requests
from typing import Optional
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# ============================================
# CONFIGURATION - Set your provider and API keys here
# ============================================

# PROVIDER OPTIONS: "ollama", "openai", "google"
PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()

# Ollama settings
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("LLM_MODEL", "llama3.2")

# OpenAI settings - Add your API key here or set OPENAI_API_KEY env var
# Example: OPENAI_API_KEY = "sk-..."
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")

# Google Gemini settings - Add your API key here or set GOOGLE_API_KEY env var
# Example: GOOGLE_API_KEY = "AIzaSy..."
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.environ.get("GOOGLE_MODEL", "gemini-1.5-pro")

# ============================================

SYSTEM_PROMPT = """You are a helpful medical health assistant. Your role is to:
1. Provide general health information and guidance
2. Help users understand their symptoms
3. Offer wellness tips and preventive care advice
4. Remind users to consult healthcare professionals for proper diagnosis

Important guidelines:
- Never provide specific medical diagnoses
- Always recommend seeing a doctor for serious symptoms
- Be empathetic and clear
- Use simple language
- If the user is describing an emergency, immediately advise them to seek emergency care
- If you don't know something, be honest about it
- Always prioritize user safety"""

def is_llm_available() -> bool:
    if PROVIDER == "ollama":
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    elif PROVIDER == "openai":
        return bool(OPENAI_API_KEY)
    elif PROVIDER == "google":
        return bool(GOOGLE_API_KEY)
    return False

def get_available_models() -> list:
    if PROVIDER == "ollama":
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except:
            pass
        return []
    elif PROVIDER == "openai":
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    elif PROVIDER == "google":
        return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    return []

def build_messages(
    conversation_history: Optional[list] = None,
    context: Optional[dict] = None
) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if conversation_history:
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    if context:
        context_str = json.dumps(context)
        messages.append({"role": "system", "content": f"Current session context: {context_str}"})
    
    return messages

def generate_response_ollama(prompt: str, messages: list) -> Optional[str]:
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("message", {}).get("content")
    except Exception as e:
        print(f"Ollama error: {e}")
    return None

def generate_response_openai(prompt: str, messages: list) -> Optional[str]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
    return None

def generate_response_google(prompt: str, messages: list) -> Optional[str]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        
        full_conversation = ""
        for msg in messages:
            if msg["role"] != "system":
                full_conversation += f"{msg['role']}: {msg['content']}\n"
        full_conversation += f"user: {prompt}"
        
        model = genai.GenerativeModel(GOOGLE_MODEL)
        response = model.generate_content(full_conversation)
        return response.text
    except Exception as e:
        print(f"Google Gemini error: {e}")
    return None

def generate_response(
    prompt: str,
    context: Optional[dict] = None,
    conversation_history: Optional[list] = None
) -> Optional[str]:
    if not is_llm_available():
        return None
    
    messages = build_messages(conversation_history, context)
    
    if PROVIDER == "ollama":
        messages.append({"role": "user", "content": prompt})
        return generate_response_ollama(prompt, messages)
    elif PROVIDER == "openai":
        return generate_response_openai(prompt, messages)
    elif PROVIDER == "google":
        return generate_response_google(prompt, messages)
    
    return None

def enhance_response(
    rule_response: dict,
    user_input: str,
    context: Optional[dict] = None,
    conversation_history: Optional[list] = None
) -> dict:
    llm_response = generate_response(
        prompt=user_input,
        context=context,
        conversation_history=conversation_history
    )
    
    if llm_response:
        rule_response["llm_enhanced"] = True
        rule_response["llm_provider"] = PROVIDER
        rule_response["message"] = llm_response
    
    return rule_response