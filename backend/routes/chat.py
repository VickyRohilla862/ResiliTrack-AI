"""
Chat routes for conversation management
"""
from flask import Blueprint, request, jsonify
from utils.auth import require_auth, get_current_user
from utils.chat_db import list_chat_messages, add_chat_message, clear_chat_messages, delete_chat_message

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/chat-history', methods=['GET'])
@require_auth
def get_chat_history():
    """
    Get chat history
    """
    try:
        user = get_current_user()
        history = list_chat_messages(user['id']) if user else []
        return jsonify({
            'history': history,
            'count': len(history)
        }), 200
    
    except Exception as e:
        print(f"Error in /chat-history: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@chat_bp.route('/chat-history', methods=['POST'])
@require_auth
def add_to_chat_history():
    """
    Add message to chat history
    
    Request body:
    {
        "message": "User message",
        "sender": "user" or "bot"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'sender' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        message_text = str(data['message']).strip()
        sender = str(data['sender']).strip()
        scenario = data.get('scenario')
        analysis_data = data.get('analysis_data')

        if not message_text or sender not in ['user', 'bot']:
            return jsonify({'error': 'Invalid message payload'}), 400

        user = get_current_user()
        message_id = add_chat_message(
            user['id'],
            message_text,
            sender,
            scenario=scenario,
            analysis_data=analysis_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Message added to history',
            'message_id': message_id
        }), 201
    
    except Exception as e:
        print(f"Error in POST /chat-history: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@chat_bp.route('/chat-history', methods=['DELETE'])
@require_auth
def clear_chat_history():
    """
    Clear chat history
    """
    try:
        user = get_current_user()
        if user:
            clear_chat_messages(user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        }), 200
    
    except Exception as e:
        print(f"Error in DELETE /chat-history: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@chat_bp.route('/chat-history/<int:message_id>', methods=['DELETE'])
@require_auth
def delete_message(message_id):
    """
    Delete a specific chat message
    """
    try:
        user = get_current_user()
        if user:
            delete_chat_message(message_id, user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Message deleted'
        }), 200
    
    except Exception as e:
        print(f"Error in DELETE /chat-history/<id>: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
