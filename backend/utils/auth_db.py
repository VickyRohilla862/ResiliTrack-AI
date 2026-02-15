import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


def _get_db_path():
    env_path = os.getenv('AUTH_DB_PATH')
    if env_path:
        return env_path
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, 'auth.db')


def _get_connection():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password_hash TEXT,
                google_sub TEXT UNIQUE,
                name TEXT,
                gemini_api_key TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def _row_to_user(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'email': row['email'],
        'name': row['name'],
        'google_sub': row['google_sub'],
        'has_api_key': bool(row['gemini_api_key'])
    }


def get_user_by_id(user_id):
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return _row_to_user(row)
    finally:
        conn.close()


def get_user_with_key(user_id):
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def get_user_by_email(email):
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()
        return _row_to_user(row)
    finally:
        conn.close()


def get_user_by_google_sub(sub):
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE google_sub = ?",
            (sub,)
        ).fetchone()
        return _row_to_user(row)
    finally:
        conn.close()


def create_email_user(email, password, name=None):
    conn = _get_connection()
    try:
        password_hash = generate_password_hash(password)
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email.lower().strip(), password_hash, name)
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    finally:
        conn.close()


def create_google_user(sub, email, name=None):
    conn = _get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (email, google_sub, name) VALUES (?, ?, ?)",
            (email.lower().strip(), sub, name)
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    finally:
        conn.close()


def update_google_sub(user_id, sub):
    conn = _get_connection()
    try:
        conn.execute(
            "UPDATE users SET google_sub = ? WHERE id = ?",
            (sub, user_id)
        )
        conn.commit()
        return get_user_by_id(user_id)
    finally:
        conn.close()


def verify_password_login(email, password):
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()
        if not row:
            return None
        if not row['password_hash']:
            return None
        if not check_password_hash(row['password_hash'], password):
            return None
        return _row_to_user(row)
    finally:
        conn.close()


def update_user_api_key(user_id, api_key):
    conn = _get_connection()
    try:
        conn.execute(
            "UPDATE users SET gemini_api_key = ? WHERE id = ?",
            (api_key.strip(), user_id)
        )
        conn.commit()
        return get_user_by_id(user_id)
    finally:
        conn.close()


def delete_user(user_id):
    conn = _get_connection()
    try:
        conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )
        conn.commit()
    finally:
        conn.close()
