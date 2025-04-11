"""
SQLAlchemy model for guild template categories.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildTemplateCategoryEntity(Base):
    """Represents a category within a guild structure template."""
    __tablename__ = 'guild_template_categories'

    id = Column(Integer, primary_key=True)
    guild_template_id = Column(Integer, ForeignKey('guild_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    category_name = Column(String(length=100), nullable=False)
    position = Column(Integer, nullable=False)
    metadata_json = Column(JSON, nullable=True)

    # Relationship back to the parent template
    guild_template = relationship("GuildTemplateEntity", back_populates="categories")

    # Relationship to channels within this template category
    channels = relationship("GuildTemplateChannelEntity", back_populates="parent_category", cascade="all, delete-orphan")

    # Relationship to permissions specific to this template category
    permissions = relationship("GuildTemplateCategoryPermissionEntity", back_populates="category_template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GuildTemplateCategoryEntity(id={self.id}, template_id={self.guild_template_id}, name='{self.category_name}')>"
