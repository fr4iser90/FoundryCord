from sqlalchemy import Column, Integer, String, BigInteger, DateTime, UniqueConstraint
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base

class ChannelMapping(Base):
    __tablename__ = 'channel_mappings'
    
    id = Column(Integer, primary_key=True)
    channel_name = Column(String, nullable=False)
    channel_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChannelMapping(name='{self.channel_name}', id={self.channel_id})>"

class CategoryMapping(Base):
    __tablename__ = 'category_mappings'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String, index=True)
    category_id = Column(String)
    category_name = Column(String)
    category_type = Column(String, default="homelab")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('guild_id', 'category_type', name='uix_category_guild_type'),
    )
    
    def __repr__(self):
        return f"<CategoryMapping(guild={self.guild_id}, type={self.category_type}, category={self.category_id})>"
