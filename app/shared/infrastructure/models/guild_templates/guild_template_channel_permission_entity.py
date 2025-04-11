"""
SQLAlchemy model for guild template channel permissions.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildTemplateChannelPermissionEntity(Base):
    """Represents a permission overwrite for a role on a template channel."""
    __tablename__ = 'guild_template_channel_permissions'

    id = Column(Integer, primary_key=True)
    channel_template_id = Column(Integer, ForeignKey('guild_template_channels.id', ondelete='CASCADE'), nullable=False, index=True)
    role_name = Column(String(length=100), nullable=False) # Storing name for resilience
    allow_permissions_bitfield = Column(BigInteger, nullable=True)
    deny_permissions_bitfield = Column(BigInteger, nullable=True)

    # Relationship back to the parent template channel
    channel_template = relationship("GuildTemplateChannelEntity", back_populates="permissions")

    def __repr__(self):
        return f"<GuildTemplateChannelPermissionEntity(id={self.id}, chan_template_id={self.channel_template_id}, role='{self.role_name}')>"
