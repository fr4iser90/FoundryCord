"""
Auto-thread channel model for Discord channels.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..base import Base

class AutoThreadChannel(Base):
    """Configuration for auto-thread channels"""
    __tablename__ = "auto_thread_channels"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False)
    channel_id = Column(String(20), nullable=False)
    thread_name_template = Column(String(100), nullable=False)
    is_private = Column(Boolean, default=False)
    auto_archive_duration = Column(Integer, default=1440)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<AutoThreadChannel(id={self.id}, channel_id='{self.channel_id}')>" 