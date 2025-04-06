from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity

class GuildRepository(ABC):
    """Abstract base class defining the interface for guild repository operations"""
    
    @abstractmethod
    async def get_by_id(self, guild_id: str) -> Optional[GuildEntity]:
        """Get a guild by its Discord ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[GuildEntity]:
        """Get all guilds"""
        pass
    
    @abstractmethod
    async def get_by_access_status(self, status: str) -> List[GuildEntity]:
        """Get all guilds with a specific access status"""
        pass
    
    @abstractmethod
    async def create(self, guild_id: str, name: str, **kwargs) -> GuildEntity:
        """Create a new guild entry"""
        pass
    
    @abstractmethod
    async def update(self, guild: GuildEntity) -> GuildEntity:
        """Update an existing guild"""
        pass
    
    @abstractmethod
    async def delete(self, guild_id: str) -> None:
        """Delete a guild"""
        pass
    
    @abstractmethod
    async def update_access_status(self, guild_id: str, status: str, reviewer_id: str = None) -> Optional[GuildEntity]:
        """Update guild access status"""
        pass
    
    @abstractmethod
    async def update_member_count(self, guild_id: str, count: int) -> Optional[GuildEntity]:
        """Update guild member count"""
        pass
    
    @abstractmethod
    async def update_settings(self, guild_id: str, settings: Dict[str, Any]) -> Optional[GuildEntity]:
        """Update guild settings"""
        pass
    
    @abstractmethod
    async def get_active_guilds(self) -> List[GuildEntity]:
        """Get all active guilds (approved status)"""
        pass
    
    @abstractmethod
    async def get_pending_guilds(self) -> List[GuildEntity]:
        """Get all pending guilds"""
        pass
    
    @abstractmethod
    async def get_blocked_guilds(self) -> List[GuildEntity]:
        """Get all blocked guilds"""
        pass
    
    @abstractmethod
    async def mark_as_joined(self, guild_id: str, joined_at: datetime = None) -> Optional[GuildEntity]:
        """Mark a guild as joined by the bot"""
        pass
    
    @abstractmethod
    async def mark_as_left(self, guild_id: str, left_at: datetime = None) -> Optional[GuildEntity]:
        """Mark a guild as left by the bot"""
        pass 