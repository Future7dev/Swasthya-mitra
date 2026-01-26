def merge_context(old, new):
    merged = old.copy()

    if new.get("symptoms"):
        merged["symptoms"] = list(set(merged.get("symptoms", []) + new["symptoms"]))

    if new.get("duration") is not None:
        merged["duration"] = new["duration"]

    if new.get("severity"):
        merged["severity"] = new["severity"]

    if new.get("intent") and new["intent"] != "unknown":
        merged["intent"] = new["intent"]

    return merged

