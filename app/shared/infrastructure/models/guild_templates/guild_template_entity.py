"""
SQLAlchemy model for guild structure templates/snapshots.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.infrastructure.models.base import Base

class GuildTemplateEntity(Base):
    """Represents a snapshot of a guild's structure."""
    __tablename__ = 'guild_templates'

    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), ForeignKey('discord_guilds.guild_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    template_name = Column(String(length=255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, server_default='true', nullable=False)

    # Relationships to template components (one-to-many)
    categories = relationship("GuildTemplateCategoryEntity", back_populates="guild_template", cascade="all, delete-orphan")
    channels = relationship("GuildTemplateChannelEntity", back_populates="guild_template", cascade="all, delete-orphan")

    # Relationship back to the original guild (optional, mainly for easy lookup)
    guild = relationship("GuildEntity", backref="structure_template") # Simple backref might be okay here

    def __repr__(self):
        return f"<GuildTemplateEntity(id={self.id}, guild_id='{self.guild_id}', name='{self.template_name}')>"
