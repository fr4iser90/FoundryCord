"""
SQLAlchemy model for guild template channels.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY for PostgreSQL
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildTemplateChannelEntity(Base):
    """Represents a channel within a guild structure template."""
    __tablename__ = 'guild_template_channels'

    id = Column(Integer, primary_key=True)
    guild_template_id = Column(Integer, ForeignKey('guild_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    channel_name = Column(String(length=100), nullable=False)
    channel_type = Column(String(length=50), nullable=False) # Store as string (e.g., 'TEXT', 'VOICE')
    position = Column(Integer, nullable=False)
    topic = Column(Text, nullable=True)
    is_nsfw = Column(Boolean, server_default='false', nullable=False)
    slowmode_delay = Column(Integer, server_default='0', nullable=False)
    is_dashboard_enabled = Column(Boolean, server_default='false', nullable=False)
    dashboard_types = Column(ARRAY(String), nullable=True, default=lambda: []) # Default to empty list
    parent_category_template_id = Column(Integer, ForeignKey('guild_template_categories.id', ondelete='SET NULL'), nullable=True, index=True)
    discord_channel_id = Column(String, nullable=True, index=True, unique=False) # Store actual Discord ID when applied/synced
    metadata_json = Column(JSON, nullable=True)

    # Relationship back to the parent template
    guild_template = relationship("GuildTemplateEntity", back_populates="channels")

    # Relationship to the parent template category
    parent_category = relationship("GuildTemplateCategoryEntity", back_populates="channels")

    # Relationship to permissions specific to this template channel
    permissions = relationship("GuildTemplateChannelPermissionEntity", back_populates="channel_template", cascade="all, delete-orphan")

    # Relationship to the dashboard instances linked to this template channel
    dashboard_instances = relationship("TemplateDashboardInstanceEntity", back_populates="channel_template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GuildTemplateChannelEntity(id={self.id}, template_id={self.guild_template_id}, name='{self.channel_name}')>"
