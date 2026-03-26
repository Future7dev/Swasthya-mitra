from utils.database import (
    create_session,
    get_session as db_get_session,
    update_session as db_update_session,
    add_message,
    get_conversation_history,
    cleanup_sessions,
    get_recent_sessions
)
import time
import threading

SESSION_TIMEOUT = 1800

_active_sessions = {}

def get_session(session_id: str):
    session = db_get_session(session_id)
    if session:
        _active_sessions[session_id] = time.time()
        if session.get("context_json"):
            try:
                import json
                session["context"] = json.loads(session["context_json"])
            except:
                session["context"] = {}
        else:
            session["context"] = {}
    return session

def create_new_session(session_id: str, user_id: str | None = None):
    create_session(session_id, user_id if user_id else None)
    _active_sessions[session_id] = time.time()

def update_session(session_id: str, context: dict, user_id: str | None = None):
    import json
    db_update_session(session_id, context, user_id if user_id else None)
    _active_sessions[session_id] = time.time()

def add_chat_message(session_id: str, role: str, content: str):
    add_message(session_id, role, content)

def get_chat_history(session_id: str, limit: int = 20):
    history = get_conversation_history(session_id, limit)
    return list(reversed(history))

def is_session_expired(session_id: str) -> bool:
    session = db_get_session(session_id)
    if not session:
        return True
    elapsed = time.time() - session.get("last_active_at", 0)
    return elapsed > SESSION_TIMEOUT

def cleanup_expired_sessions():
    deleted = cleanup_sessions(86400)
    for sid in list(_active_sessions.keys()):
        if is_session_expired(sid):
            _active_sessions.pop(sid, None)
    return deleted

def start_cleanup_scheduler():
    def run():
        while True:
            time.sleep(3600)
            cleanup_expired_sessions()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

start_cleanup_scheduler()