"""
Guild model for Discord servers.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.shared.infrastructure.models.base import Base
from datetime import datetime

class GuildEntity(Base):
    """Entity representing a Discord guild/server"""
    __tablename__ = 'discord_guilds'

    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon_url = Column(String(255), nullable=True)
    owner_id = Column(String(20), nullable=True)
    member_count = Column(Integer, default=0)
    joined_at = Column(DateTime, nullable=False, server_default='now()')
    settings = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Access Control Fields
    access_status = Column(String(20), nullable=False, server_default='PENDING')
    access_requested_at = Column(DateTime, server_default='now()', nullable=False)
    access_reviewed_at = Column(DateTime, nullable=True)
    access_reviewed_by = Column(String(32), nullable=True)
    access_notes = Column(Text, nullable=True)
    
    # Bot Integration Settings
    enable_commands = Column(Boolean, nullable=False, server_default='false')
    enable_logging = Column(Boolean, nullable=False, server_default='true')
    enable_automod = Column(Boolean, nullable=False, server_default='false')
    enable_welcome = Column(Boolean, nullable=False, server_default='false')

    def __repr__(self):
        return f"<GuildEntity(id={self.id}, name='{self.name}', status='{self.access_status}')>"