from abc import ABC, abstractmethod
from typing import Optional, List
from app.shared.infrastructure.models.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
        
    @abstractmethod
    async def get_by_discord_id(self, discord_id: str) -> Optional[User]:
        """Get user by Discord ID"""
        pass
        
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user"""
        pass
        
    @abstractmethod
    async def get_all_by_role(self, role_name: str) -> List[User]:
        """Get all users with specified role"""
        pass