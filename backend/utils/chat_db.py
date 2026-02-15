import os
import sqlite3
import json


def _get_db_path():
    env_path = os.getenv('CHAT_DB_PATH')
    if env_path:
        return env_path
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, 'chat.db')


def _get_connection():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_chat_db():
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                scenario TEXT,
                analysis_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_chat_message(user_id, message, sender, scenario=None, analysis_data=None):
    analysis_json = None
    if analysis_data is not None:
        analysis_json = json.dumps(analysis_data, ensure_ascii=True)
    conn = _get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO chat_messages (user_id, message, sender, scenario, analysis_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, message, sender, scenario, analysis_json)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_chat_messages(user_id):
    conn = _get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, message, sender, scenario, analysis_json, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY id ASC
            """,
            (user_id,)
        ).fetchall()
        messages = []
        for row in rows:
            analysis_data = None
            if row['analysis_json']:
                try:
                    analysis_data = json.loads(row['analysis_json'])
                except json.JSONDecodeError:
                    analysis_data = None
            messages.append({
                'id': row['id'],
                'message': row['message'],
                'sender': row['sender'],
                'scenario': row['scenario'],
                'analysis_data': analysis_data,
                'created_at': row['created_at']
            })
        return messages
    finally:
        conn.close()


def clear_chat_messages(user_id):
    conn = _get_connection()
    try:
        conn.execute(
            "DELETE FROM chat_messages WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
    finally:
        conn.close()


def delete_chat_message(message_id, user_id):
    conn = _get_connection()
    try:
        conn.execute(
            "DELETE FROM chat_messages WHERE id = ? AND user_id = ?",
            (message_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()
