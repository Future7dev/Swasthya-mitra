import json
from pathlib import Path 

BASE_DIR = Path(__file__).resolve().parent.parent 
RULES_DIR = BASE_DIR / "rules" 

def load_symptoms():
    with open(RULES_DIR / "symptoms.json") as f:
        return json.load(f)

def load_emergencies():
    with open(RULES_DIR / "emergencies.json") as f:
        return json.load(f)
