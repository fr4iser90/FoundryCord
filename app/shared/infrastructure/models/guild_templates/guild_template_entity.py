"""
SQLAlchemy model for guild structure templates/snapshots.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.infrastructure.models.base import Base
# Import AppUserEntity for the foreign key
from app.shared.infrastructure.models.auth import AppUserEntity

class GuildTemplateEntity(Base):
    """Represents a snapshot of a guild's structure.
    Can be an initial snapshot (guild_id unique, creator_user_id NULL)
    or a user-saved template (guild_id not necessarily unique, creator_user_id set).
    """
    __tablename__ = 'guild_templates'

    id = Column(Integer, primary_key=True)
    # guild_id is the original source, not necessarily unique anymore
    guild_id = Column(String(20), ForeignKey('discord_guilds.guild_id', ondelete='SET NULL'), nullable=True, index=True)
    template_name = Column(String(length=255), nullable=False)
    # Add creator user ID (nullable for bot-created snapshots)
    creator_user_id = Column(Integer, ForeignKey('app_users.id', ondelete='SET NULL'), nullable=True, index=True)
    # Add shared flag
    is_shared = Column(Boolean, server_default='false', nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, server_default='true', nullable=False)

    # Relationships to template components (one-to-many)
    categories = relationship("GuildTemplateCategoryEntity", back_populates="guild_template", cascade="all, delete-orphan")
    channels = relationship("GuildTemplateChannelEntity", back_populates="guild_template", cascade="all, delete-orphan")

    # Relationship back to the original guild (optional, mainly for easy lookup)
    # Use optional=True if guild_id can be NULL
    guild = relationship("GuildEntity", backref="structure_template") 
    # Relationship to the creator user
    creator = relationship("AppUserEntity")

    def __repr__(self):
        creator_info = f", creator={self.creator_user_id}" if self.creator_user_id else ""
        guild_info = f", source_guild={self.guild_id}" if self.guild_id else ""
        shared_info = " [SHARED]" if self.is_shared else ""
        return f"<GuildTemplateEntity(id={self.id}, name='{self.template_name}'{creator_info}{guild_info}{shared_info})>"

    # Remove unique constraint on guild_id if users can save multiple templates from same guild
    # If initial snapshots should still be unique per guild, need different logic.
    # Assuming users can save freely, remove the constraint implicitly by not defining it.
    # __table_args__ = (UniqueConstraint('guild_id', name='_guild_template_uc'),)
