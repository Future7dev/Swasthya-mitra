import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "healthbot.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at REAL NOT NULL,
            last_active_at REAL NOT NULL,
            context_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_session 
        ON conversations(session_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_last_active 
        ON sessions(last_active_at)
    """)

    conn.commit()
    conn.close()

def create_session(session_id: str, user_id: str | None = None):
    now = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sessions 
        (session_id, user_id, created_at, last_active_at, context_json)
        VALUES (?, ?, ?, ?, '{}')
    """, (session_id, user_id, now, now))
    conn.commit()
    conn.close()

def get_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sessions WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_session(session_id: str, context: dict, user_id: str | None = None):
    now = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    import json
    cursor.execute("""
        INSERT OR REPLACE INTO sessions 
        (session_id, user_id, created_at, last_active_at, context_json)
        SELECT session_id, ?, created_at, ?, ? FROM sessions 
        WHERE session_id = ?
        UNION ALL
        SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM sessions WHERE session_id = ?)
    """, (user_id, now, json.dumps(context), session_id, session_id, user_id, now, now, json.dumps(context), session_id))
    conn.commit()
    conn.close()

def add_message(session_id: str, role: str, content: str):
    now = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, now))
    conn.commit()
    conn.close()

def get_conversation_history(session_id: str, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, timestamp FROM conversations
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def cleanup_sessions(max_age_seconds: int = 86400):
    now = time.time()
    cutoff = now - max_age_seconds
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM conversations WHERE session_id IN (
            SELECT session_id FROM sessions WHERE last_active_at < ?
        )
    """, (cutoff,))
    cursor.execute("""
        DELETE FROM sessions WHERE last_active_at < ?
    """, (cutoff,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted

def get_recent_sessions(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, user_id, last_active_at FROM sessions
        ORDER BY last_active_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

init_db()