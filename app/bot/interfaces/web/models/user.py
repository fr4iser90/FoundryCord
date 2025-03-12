from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """
    User model for the web interface
    """
    id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @property
    def avatar_full_url(self) -> str:
        """
        Get the full Discord avatar URL
        """
        if not self.avatar_url:
            return f"https://cdn.discordapp.com/embed/avatars/0.png"
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_url}.png" 