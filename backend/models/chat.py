from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Message:
    id: int
    chat_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class Chat:
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[Message]] = None
    
    def to_dict(self) -> dict:
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if self.messages:
            result['messages'] = [msg.to_dict() for msg in self.messages]
            
        return result
    
    def get_preview(self) -> str:
        """Get first message as preview"""
        if self.messages and len(self.messages) > 0:
            return self.messages[0].content[:50] + '...'
        return 'New Chat'
