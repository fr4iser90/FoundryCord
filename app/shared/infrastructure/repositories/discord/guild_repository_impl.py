from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from app.shared.domain.repositories.discord.guild_repository import GuildRepository
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

# String constants for access status
ACCESS_PENDING = "pending"
ACCESS_APPROVED = "approved"
ACCESS_REJECTED = "rejected"
ACCESS_SUSPENDED = "suspended"

class GuildRepositoryImpl(GuildRepository):
    """Implementation of the Guild repository for Discord server management"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, guild_id: str) -> Optional[GuildEntity]:
        """Get a guild by its Discord ID"""
        result = await self.session.execute(
            select(GuildEntity).where(GuildEntity.guild_id == guild_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[GuildEntity]:
        """Get all guilds"""
        result = await self.session.execute(select(GuildEntity))
        return result.scalars().all()
    
    async def get_by_access_status(self, status: str) -> List[GuildEntity]:
        """Get all guilds with a specific access status"""
        result = await self.session.execute(
            select(GuildEntity).where(GuildEntity.access_status == status)
        )
        return result.scalars().all()
    
    async def create(self, guild_id: str, name: str, **kwargs) -> GuildEntity:
        """Create a new guild entry"""
        guild = GuildEntity(
            guild_id=guild_id,
            name=name,
            owner_id=kwargs.get('owner_id'),
            icon_url=kwargs.get('icon_url'),
            member_count=kwargs.get('member_count', 0),
            access_status=kwargs.get('access_status', ACCESS_PENDING),
            access_requested_at=kwargs.get('access_requested_at', datetime.utcnow()),
            settings=kwargs.get('settings')
        )
        self.session.add(guild)
        await self.session.commit()
        return guild
    
    async def update(self, guild: GuildEntity) -> GuildEntity:
        """Update an existing guild"""
        self.session.add(guild)
        await self.session.commit()
        return guild
    
    async def delete(self, guild_id: str) -> None:
        """Delete a guild"""
        guild = await self.get_by_id(guild_id)
        if guild:
            await self.session.delete(guild)
            await self.session.commit()
    
    async def create_or_update(self, guild_id: str, name: str, **kwargs) -> GuildEntity:
        """Create a new guild or update if it already exists"""
        existing = await self.get_by_id(guild_id)
        
        if existing:
            # Update existing guild
            existing.name = name
            existing.owner_id = kwargs.get('owner_id', existing.owner_id)
            existing.icon_url = kwargs.get('icon_url', existing.icon_url)
            existing.member_count = kwargs.get('member_count', existing.member_count)
            existing.settings = kwargs.get('settings', existing.settings)
            
            # Only update access_status if explicitly provided
            if 'access_status' in kwargs:
                existing.access_status = kwargs['access_status']
                
            self.session.add(existing)
            await self.session.commit()
            return existing
        else:
            # Create new guild with default PENDING status if not specified
            if 'access_status' not in kwargs:
                kwargs['access_status'] = ACCESS_PENDING
            return await self.create(guild_id, name, **kwargs)
    
    async def update_access_status(self, guild_id: str, status: str, reviewer_id: str = None) -> Optional[GuildEntity]:
        """Update guild access status"""
        guild = await self.get_by_id(guild_id)
        if guild:
            guild.access_status = status
            guild.access_reviewed_at = datetime.utcnow()
            guild.access_reviewed_by = reviewer_id
            await self.session.commit()
            return guild
        return None
    
    async def update_member_count(self, guild_id: str, count: int) -> Optional[GuildEntity]:
        """Update guild member count"""
        guild = await self.get_by_id(guild_id)
        if guild:
            guild.member_count = count
            await self.session.commit()
            return guild
        return None
    
    async def update_settings(self, guild_id: str, settings: Dict[str, Any]) -> Optional[GuildEntity]:
        """Update guild settings"""
        guild = await self.get_by_id(guild_id)
        if guild:
            guild.settings = settings
            await self.session.commit()
            return guild
        return None
    
    async def get_active_guilds(self) -> List[GuildEntity]:
        """Get all active guilds (approved status)"""
        return await self.get_by_access_status(ACCESS_APPROVED)
    
    async def get_pending_guilds(self) -> List[GuildEntity]:
        """Get all pending guilds"""
        return await self.get_by_access_status(ACCESS_PENDING)
    
    async def get_blocked_guilds(self) -> List[GuildEntity]:
        """Get all blocked guilds"""
        return await self.get_by_access_status(ACCESS_SUSPENDED)
    
    async def mark_as_joined(self, guild_id: str, joined_at: datetime = None) -> Optional[GuildEntity]:
        """Mark a guild as joined"""
        guild = await self.get_by_id(guild_id)
        if guild:
            guild.joined_at = joined_at or datetime.utcnow()
            guild.is_active = True
            await self.session.commit()
            return guild
        return None
    
    async def mark_as_left(self, guild_id: str, left_at: datetime = None) -> Optional[GuildEntity]:
        """Mark a guild as left"""
        guild = await self.get_by_id(guild_id)
        if guild:
            guild.is_active = False
            await self.session.commit()
            return guild
        return None 