from functools import wraps
from flask import session, g, jsonify
from .auth_db import get_user_by_id, get_user_with_key


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_user_by_id(user_id)


def get_current_user_with_key():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_user_with_key(user_id)


def require_auth(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        g.user = user
        return handler(*args, **kwargs)
    return wrapper
