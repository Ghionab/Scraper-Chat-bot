from flask import Blueprint, request, jsonify
from functools import wraps
from backend.routes.auth import require_auth
from backend.utils.db import (
    create_chat, get_user_chats, get_chat_messages, add_message,
    update_chat_timestamp, save_chat_metadata, get_chat_metadata, get_db
)
from backend.utils.scraper import WebScraper
from backend.utils.openai_helper import OpenAIHelper

chat_bp = Blueprint('chat', __name__)

# Initialize scraper and OpenAI helper
scraper = WebScraper()
openai_helper = OpenAIHelper()


# Error handling decorator
def handle_errors(f):
    """
    Decorator to handle errors in chat endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    return decorated_function


# Helper function to verify chat ownership
def verify_chat_ownership(chat_id: str, user_id: int) -> bool:
    """
    Verify that a chat belongs to a specific user
    
    Args:
        chat_id: Chat session ID
        user_id: User ID
        
    Returns:
        True if user owns the chat, False otherwise
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM chats WHERE id = ?', (chat_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row['user_id'] == user_id:
        return True
    return False


# Chat endpoints

@chat_bp.route('/message', methods=['POST'])
@require_auth
@handle_errors
def send_message():
    """
    Send a message in a chat session
    
    Request Body:
        {
            "chat_id": "uuid-string" (optional, creates new chat if not provided),
            "url": "https://example.com" (optional),
            "prompt": "What information do you need?"
        }
    
    Response:
        {
            "success": true,
            "response": "AI response text",
            "chat_id": "uuid-string"
        }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'success': False, 'error': 'Prompt is required'}), 400
    
    chat_id = data.get('chat_id')
    url = data.get('url', '').strip()
    user_id = request.current_user_id
    
    # Get or create chat session
    if chat_id:
        # Verify chat ownership
        if not verify_chat_ownership(chat_id, user_id):
            return jsonify({'success': False, 'error': 'Chat not found or access denied'}), 404
    else:
        # Create new chat session
        chat_id = create_chat(user_id)
    
    # Get previous messages for conversation context
    previous_messages = get_chat_messages(chat_id)
    conversation_history = [
        {"role": msg['role'], "content": msg['content']}
        for msg in previous_messages
    ]
    
    # Handle web scraping
    website_content = None
    if url:
        # Scrape the new URL
        scrape_result = scraper.scrape_sync(url)
        
        if not scrape_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to scrape website: {scrape_result['error']}"
            }), 400
        
        website_content = scrape_result['content']
        
        # Save the scraped content to metadata
        save_chat_metadata(chat_id, url, website_content)
    else:
        # Check if we have cached content from previous scrape
        metadata = get_chat_metadata(chat_id)
        if metadata and metadata.get('last_scraped_content'):
            website_content = metadata['last_scraped_content']
    
    # Generate AI response
    ai_result = openai_helper.generate_response(
        user_prompt=prompt,
        website_content=website_content,
        conversation_history=conversation_history
    )
    
    if not ai_result['success']:
        return jsonify({
            'success': False,
            'error': f"Failed to generate response: {ai_result['error']}"
        }), 500
    
    # Save user message
    add_message(chat_id, 'user', prompt)
    
    # Save AI response
    add_message(chat_id, 'assistant', ai_result['response'])
    
    # Update chat timestamp
    update_chat_timestamp(chat_id)
    
    return jsonify({
        'success': True,
        'response': ai_result['response'],
        'chat_id': chat_id
    }), 200


@chat_bp.route('/history', methods=['GET'])
@require_auth
@handle_errors
def get_history():
    """
    Get all chat sessions for the authenticated user
    
    Response:
        {
            "success": true,
            "chats": [
                {
                    "chat_id": "uuid-string",
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:30:00",
                    "preview": "First message preview..."
                }
            ]
        }
    """
    user_id = request.current_user_id
    
    # Get all chats for user
    chats = get_user_chats(user_id)
    
    # Add preview for each chat
    chat_list = []
    for chat in chats:
        messages = get_chat_messages(chat['id'])
        preview = 'New Chat'
        
        if messages and len(messages) > 0:
            # Use first user message as preview
            first_message = messages[0]['content']
            preview = first_message[:50] + ('...' if len(first_message) > 50 else '')
        
        chat_list.append({
            'chat_id': chat['id'],
            'created_at': chat['created_at'],
            'updated_at': chat['updated_at'],
            'preview': preview
        })
    
    return jsonify({
        'success': True,
        'chats': chat_list
    }), 200


@chat_bp.route('/<chat_id>', methods=['GET'])
@require_auth
@handle_errors
def get_chat(chat_id):
    """
    Get a specific chat session with all messages
    
    Response:
        {
            "success": true,
            "chat_id": "uuid-string",
            "messages": [
                {
                    "id": 1,
                    "role": "user",
                    "content": "Message content",
                    "timestamp": "2024-01-01T12:00:00"
                }
            ]
        }
    """
    user_id = request.current_user_id
    
    # Verify chat ownership
    if not verify_chat_ownership(chat_id, user_id):
        return jsonify({'success': False, 'error': 'Chat not found or access denied'}), 404
    
    # Get all messages for the chat
    messages = get_chat_messages(chat_id)
    
    return jsonify({
        'success': True,
        'chat_id': chat_id,
        'messages': messages
    }), 200


@chat_bp.route('/new', methods=['POST'])
@require_auth
@handle_errors
def new_chat():
    """
    Create a new chat session
    
    Response:
        {
            "success": true,
            "chat_id": "uuid-string"
        }
    """
    user_id = request.current_user_id
    
    # Create new chat session
    chat_id = create_chat(user_id)
    
    return jsonify({
        'success': True,
        'chat_id': chat_id
    }), 201
