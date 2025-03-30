"""
Channel mapping model for Discord channels.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.shared.infrastructure.models.base import Base

class ChannelMapping(Base):
    """Mapping between channel names and Discord channel IDs"""
    __tablename__ = "channel_mappings"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False)
    channel_id = Column(String(20), nullable=False)
    channel_name = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)
    parent_channel_id = Column(String(20), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Behavior flags
    delete_on_shutdown = Column(Boolean, default=False, nullable=False)
    create_on_startup = Column(Boolean, default=True, nullable=False)
    sync_permissions = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ChannelMapping(id={self.id}, type='{self.channel_type}', name='{self.channel_name}')>" 