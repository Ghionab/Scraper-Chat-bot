from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    username: str
    password_hash: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary (exclude password_hash)"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def from_db_row(row) -> 'User':
        """Create User from database row"""
        return User(
            id=row['id'],
            email=row['email'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
