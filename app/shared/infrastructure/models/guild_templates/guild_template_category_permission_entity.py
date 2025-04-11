"""
SQLAlchemy model for guild template category permissions.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildTemplateCategoryPermissionEntity(Base):
    """Represents a permission overwrite for a role on a template category."""
    __tablename__ = 'guild_template_category_permissions'

    id = Column(Integer, primary_key=True)
    category_template_id = Column(Integer, ForeignKey('guild_template_categories.id', ondelete='CASCADE'), nullable=False, index=True)
    role_name = Column(String(length=100), nullable=False) # Storing name for resilience
    allow_permissions_bitfield = Column(BigInteger, nullable=True)
    deny_permissions_bitfield = Column(BigInteger, nullable=True)

    # Relationship back to the parent template category
    category_template = relationship("GuildTemplateCategoryEntity", back_populates="permissions")

    def __repr__(self):
        return f"<GuildTemplateCategoryPermissionEntity(id={self.id}, cat_template_id={self.category_template_id}, role='{self.role_name}')>"
