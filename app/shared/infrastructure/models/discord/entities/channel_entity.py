from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base
from app.shared.infrastructure.models.discord.enums.channels import ChannelType, ChannelPermissionLevel

class ChannelEntity(Base):
    """Database entity for Discord channels"""
    __tablename__ = "discord_channels"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, nullable=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("discord_categories.id"), nullable=True)
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
    
    # Verwende String-Referenz zur Vermeidung zirkulärer Importe
    category = relationship("CategoryEntity", back_populates="channels")
    permissions = relationship("ChannelPermissionEntity", back_populates="channel", 
                              cascade="all, delete-orphan")


class ChannelPermissionEntity(Base):
    """Database entity for channel permissions"""
    __tablename__ = "discord_channel_permissions"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("discord_channels.id"), nullable=False)
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
    
    # Only define the relationship to ChannelEntity, remove any Role relationship
    channel = relationship("ChannelEntity", back_populates="permissions")
    
    # Remove any back_populates to guild_users or roles - this is likely causing the error 