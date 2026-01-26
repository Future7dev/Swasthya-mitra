from collections import defaultdict

_sessions = defaultdict(dict)

def get_session(session_id: str):
	return _sessions[session_id]

def update_session(session_id: str, data: dict):
    _sessions[session_id].update(data)
