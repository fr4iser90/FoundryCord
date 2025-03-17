"""
Message model for Discord messages.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class Message(Base):
    """Discord message tracking model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(20), unique=True, nullable=False)
    guild_id = Column(String(20), nullable=False, index=True)
    channel_id = Column(String(20), nullable=False, index=True)
    author_id = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Message(id={self.id}, message_id={self.message_id})>" 