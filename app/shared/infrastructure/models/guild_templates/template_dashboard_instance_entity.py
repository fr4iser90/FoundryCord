"""
SQLAlchemy model for dashboard instances defined within guild templates.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.infrastructure.models import Base # Assuming Base is defined here

class TemplateDashboardInstanceEntity(Base):
    """Represents a dashboard instance defined within a guild template channel."""
    __tablename__ = "dashboard_instances"

    id = Column(Integer, primary_key=True)
    # Foreign key to the specific channel within the template
    guild_template_channel_id = Column(Integer, ForeignKey('guild_template_channels.id', ondelete='CASCADE'), nullable=False, index=True)
    dashboard_type = Column(String(100), nullable=False, comment="Functional type from DASHBOARD_MAPPINGS")
    name = Column(String(100), nullable=False, comment="User-defined name for this instance")
    config = Column(JSON, nullable=True, comment="Specific configuration for this instance")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Define the relationship back to the GuildTemplateChannelEntity
    # The back_populates name must match the relationship name defined in GuildTemplateChannelEntity
    channel_template = relationship("GuildTemplateChannelEntity", back_populates="dashboard_instances") 

    def __repr__(self):
        return f"<TemplateDashboardInstanceEntity(id={self.id}, name='{self.name}', type='{self.dashboard_type}', channel_template_id={self.guild_template_channel_id})>" 