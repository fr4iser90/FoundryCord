"""
Guild model for Discord servers.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from ..base import Base

class Guild(Base):
    """Discord guild model"""
    __tablename__ = "guilds"
    
    id = Column(Integer, primary_key=True)  # Primärschlüssel hinzugefügt
    guild_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon_url = Column(String(255), nullable=True)
    owner_id = Column(String(20), nullable=True)
    member_count = Column(Integer, default=0)
    joined_at = Column(DateTime, nullable=False, server_default=func.now())
    settings = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Guild(id={self.id}, name='{self.name}')>"