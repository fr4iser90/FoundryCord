from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from app.shared.infrastructure.models import RateLimitEntity

class RateLimitRepository(ABC):
    @abstractmethod
    async def get_by_id(self, rate_limit_id: int) -> Optional[RateLimitEntity]:
        """Get a rate limit by ID"""
        pass

    @abstractmethod
    async def get_by_user_and_command(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        """Get rate limit for a specific user and command"""
        pass

    @abstractmethod
    async def get_blocked_commands(self, user_id: str) -> List[RateLimitEntity]:
        """Get all blocked commands for a user"""
        pass

    @abstractmethod
    async def create_or_update(self, user_id: str, command_type: str, 
                              increment_count: bool = True) -> RateLimitEntity:
        """Create or update a rate limit entry"""
        pass

    @abstractmethod
    async def set_block(self, user_id: str, command_type: str, blocked_until: datetime) -> RateLimitEntity:
        """Set a block on a command for a user"""
        pass

    @abstractmethod
    async def clear_block(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        """Clear a block for a user and command"""
        pass

    @abstractmethod
    async def reset_count(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        """Reset attempt count for a user and command"""
        pass

    @abstractmethod
    async def delete(self, rate_limit: RateLimitEntity) -> None:
        """Delete a rate limit entry"""
        pass 