from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.shared.infrastructure.database.models.base import Base
from app.shared.domain.models.discord.channel_model import ChannelType, ChannelPermissionLevel

class ChannelEntity(Base):
    """Database entity for Discord channels"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, nullable=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category_discord_id = Column(BigInteger, nullable=True)
    type = Column(Enum(ChannelType), nullable=False, default=ChannelType.TEXT)
    position = Column(Integer, nullable=False, default=0)
    permission_level = Column(Enum(ChannelPermissionLevel), nullable=False, 
                              default=ChannelPermissionLevel.PUBLIC)
    is_enabled = Column(Boolean, nullable=False, default=True)
    is_created = Column(Boolean, nullable=False, default=False)
    nsfw = Column(Boolean, nullable=False, default=False)
    slowmode_delay = Column(Integer, nullable=False, default=0)
    topic = Column(String, nullable=True)
    thread_config = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    # Relationships
    category = relationship("CategoryEntity", back_populates="channels")
    permissions = relationship("ChannelPermissionEntity", back_populates="channel", 
                              cascade="all, delete-orphan")


class ChannelPermissionEntity(Base):
    """Database entity for channel permissions"""
    __tablename__ = "channel_permissions"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    role_id = Column(BigInteger, nullable=False)
    view = Column(Boolean, nullable=False, default=False)
    send_messages = Column(Boolean, nullable=False, default=False)
    read_messages = Column(Boolean, nullable=False, default=False)
    manage_messages = Column(Boolean, nullable=False, default=False)
    manage_channel = Column(Boolean, nullable=False, default=False)
    use_bots = Column(Boolean, nullable=False, default=False)
    embed_links = Column(Boolean, nullable=False, default=False)
    attach_files = Column(Boolean, nullable=False, default=False)
    add_reactions = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    channel = relationship("ChannelEntity", back_populates="permissions") 