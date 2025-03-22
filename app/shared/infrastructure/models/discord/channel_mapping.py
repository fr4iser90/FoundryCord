"""
Channel mapping model for Discord channels.
"""
from sqlalchemy import Column, Integer, String, BigInteger
from ..base import Base

class ChannelMapping(Base):
    """Mapping between channel names and Discord channel IDs"""
    __tablename__ = "channel_mappings"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False)
    channel_id = Column(String(20), nullable=False)
    channel_name = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)
    parent_channel_id = Column(BigInteger, nullable=True)
    
    def __repr__(self):
        return f"<ChannelMapping(id={self.id}, type='{self.channel_type}', name='{self.channel_name}')>" 