import sqlite3
from datetime import datetime
import uuid
from typing import Optional, List, Dict, Any

DATABASE = 'database.db'


def get_db() -> sqlite3.Connection:
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def sanitize_db_input(text: str) -> str:
    """
    Sanitize input before database insertion
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ''
    
    # Remove null bytes which can cause issues with SQLite
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def init_db() -> None:
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    ''')
    
    # Chat metadata table (for storing scraped URLs per chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_metadata (
            chat_id TEXT PRIMARY KEY,
            last_url TEXT,
            last_scraped_content TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    ''')
    
    conn.commit()
    conn.close()


# User operations

def create_user(email: str, username: str, password_hash: str) -> int:
    """
    Create a new user
    
    Args:
        email: User's email address
        username: User's username
        password_hash: Hashed password
        
    Returns:
        User ID of the created user
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Sanitize inputs
    email = sanitize_db_input(email)
    username = sanitize_db_input(username)
    
    cursor.execute(
        'INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',
        (email, username, password_hash)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user by email address
    
    Args:
        email: User's email address
        
    Returns:
        Dictionary containing user data or None if not found
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user by ID
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary containing user data or None if not found
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


# Chat operations

def create_chat(user_id: int) -> str:
    """
    Create a new chat session
    
    Args:
        user_id: ID of the user creating the chat
        
    Returns:
        Chat ID (UUID string)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    chat_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        'INSERT INTO chats (id, user_id, created_at, updated_at) VALUES (?, ?, ?, ?)',
        (chat_id, user_id, timestamp, timestamp)
    )
    
    conn.commit()
    conn.close()
    
    return chat_id


def get_user_chats(user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all chat sessions for a user
    
    Args:
        user_id: User's ID
        
    Returns:
        List of dictionaries containing chat data
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM chats WHERE user_id = ? ORDER BY updated_at DESC',
        (user_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_chat_messages(chat_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all messages for a chat session
    
    Args:
        chat_id: Chat session ID
        
    Returns:
        List of dictionaries containing message data
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp ASC',
        (chat_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def add_message(chat_id: str, role: str, content: str) -> None:
    """
    Add a message to a chat session
    
    Args:
        chat_id: Chat session ID
        role: Message role ('user' or 'assistant')
        content: Message content
    """
    conn = get_db()
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    # Sanitize content (chat_id and role are controlled by the application)
    content = sanitize_db_input(content)
    
    cursor.execute(
        'INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
        (chat_id, role, content, timestamp)
    )
    
    conn.commit()
    conn.close()


def update_chat_timestamp(chat_id: str) -> None:
    """
    Update the updated_at timestamp for a chat session
    
    Args:
        chat_id: Chat session ID
    """
    conn = get_db()
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        'UPDATE chats SET updated_at = ? WHERE id = ?',
        (timestamp, chat_id)
    )
    
    conn.commit()
    conn.close()


# Chat metadata operations

def save_chat_metadata(chat_id: str, url: str, content: str) -> None:
    """
    Save or update chat metadata (last scraped URL and content)
    
    Args:
        chat_id: Chat session ID
        url: Last scraped URL
        content: Last scraped content
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Sanitize inputs (chat_id is controlled by the application)
    url = sanitize_db_input(url)
    content = sanitize_db_input(content)
    
    # Use INSERT OR REPLACE to handle both insert and update
    cursor.execute(
        'INSERT OR REPLACE INTO chat_metadata (chat_id, last_url, last_scraped_content) VALUES (?, ?, ?)',
        (chat_id, url, content)
    )
    
    conn.commit()
    conn.close()


def get_chat_metadata(chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve chat metadata
    
    Args:
        chat_id: Chat session ID
        
    Returns:
        Dictionary containing metadata or None if not found
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM chat_metadata WHERE chat_id = ?', (chat_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None
