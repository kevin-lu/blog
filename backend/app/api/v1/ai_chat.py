"""
AI Chat API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.config import Config
import requests
import re
import json

bp = Blueprint('ai_chat', __name__)


@bp.route('/chat', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def chat():
    """
    AI Chat endpoint
    
    Request JSON:
        {
            "message": "用户输入的问题或对话内容",
            "conversation_history": [
                {"role": "user", "content": "之前的问题"},
                {"role": "assistant", "content": "之前的回答"}
            ]
        }
    
    Returns:
        {
            "reply": "AI 助手的回复内容",
            "model": "MiniMax-M2.7",
            "usage": {
                "total_tokens": 150
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    message = data.get('message')
    conversation_history = data.get('conversation_history', [])
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Build messages for MiniMax API
    messages = []
    
    # Add conversation history if provided
    if conversation_history and isinstance(conversation_history, list):
        for msg in conversation_history[-10:]:  # Limit to last 10 messages
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
    
    # Add current message
    messages.append({
        'role': 'user',
        'content': message
    })
    
    # Call MiniMax API
    try:
        api_key = Config.MINIMAX_API_KEY
        api_host = Config.MINIMAX_API_HOST
        model = Config.MINIMAX_MODEL
        timeout = Config.MINIMAX_REQUEST_TIMEOUT
        
        if not api_key:
            return jsonify({'error': 'AI API key not configured'}), 500
        
        payload = {
            'model': model,
            'messages': messages,
            'stream': False,
            'temperature': 0.7,
            'max_tokens': 2048
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            api_host,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': f'AI API error: {response.status_code}'
            }), 500
        
        result = response.json()
        
        # Parse MiniMax response
        if 'choices' in result and len(result['choices']) > 0:
            reply = result['choices'][0]['message']['content']
            
            # Remove think tags and content
            reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
            
            usage = result.get('usage', {})
            
            return jsonify({
                'reply': reply,
                'model': model,
                'usage': {
                    'total_tokens': usage.get('total_tokens', 0)
                }
            }), 200
        else:
            return jsonify({
                'error': 'No response from AI'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'AI request timeout, please try again'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to connect to AI service: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Internal error: {str(e)}'
        }), 500
