from flask import Blueprint, request, jsonify, session, current_app
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from utils.auth_db import (
    get_user_by_email,
    get_user_by_google_sub,
    create_email_user,
    create_google_user,
    verify_password_login,
    update_google_sub,
    update_user_api_key,
    delete_user
)
from utils.chat_db import clear_chat_messages
from utils.auth import get_current_user, require_auth


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _sanitize_email(email):
    return (email or '').strip().lower()


def _build_user_payload(user):
    if not user:
        return None
    return {
        'id': user['id'],
        'email': user.get('email'),
        'name': user.get('name'),
        'has_api_key': bool(user.get('has_api_key'))
    }


def _set_session_user(user):
    session['user_id'] = user['id']
    session.permanent = True


@auth_bp.route('/me', methods=['GET'])
def me():
    user = get_current_user()
    if not user:
        return jsonify({'authenticated': False}), 200
    return jsonify({'authenticated': True, 'user': _build_user_payload(user)}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = _sanitize_email(data.get('email'))
    password = data.get('password') or ''
    name = (data.get('name') or '').strip() or None

    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if get_user_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409

    user = create_email_user(email, password, name)
    _set_session_user(user)
    return jsonify({'success': True, 'user': _build_user_payload(user)}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = _sanitize_email(data.get('email'))
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = verify_password_login(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    _set_session_user(user)
    return jsonify({'success': True, 'user': _build_user_payload(user)}), 200


@auth_bp.route('/google', methods=['POST'])
def google_login():
    data = request.get_json() or {}
    credential = data.get('credential')

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not client_id or client_id == 'YOUR_GOOGLE_CLIENT_ID':
        return jsonify({'error': 'Google login is not configured'}), 503

    if not credential:
        return jsonify({'error': 'Missing Google credential'}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id
        )
        sub = idinfo.get('sub')
        email = _sanitize_email(idinfo.get('email'))
        name = (idinfo.get('name') or '').strip() or None

        if not sub or not email:
            return jsonify({'error': 'Invalid Google profile'}), 400

        user = get_user_by_google_sub(sub)
        if not user:
            existing = get_user_by_email(email)
            if existing:
                user = update_google_sub(existing['id'], sub)
            else:
                user = create_google_user(sub, email, name)

        _set_session_user(user)
        return jsonify({'success': True, 'user': _build_user_payload(user)}), 200
    except ValueError:
        return jsonify({'error': 'Invalid Google token'}), 401


@auth_bp.route('/api-key', methods=['POST'])
@require_auth
def set_api_key():
    data = request.get_json() or {}
    api_key = (data.get('api_key') or '').strip()

    if len(api_key) < 20:
        return jsonify({'error': 'API key looks invalid'}), 400

    user = update_user_api_key(session['user_id'], api_key)
    return jsonify({'success': True, 'user': _build_user_payload(user)}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200


@auth_bp.route('/account', methods=['DELETE'])
@require_auth
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        clear_chat_messages(user_id)
        delete_user(user_id)
        session.clear()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete account'}), 500
