"""SQLAlchemy model for active dashboard instances."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import BIGINT, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class ActiveDashboardEntity(Base):
    """Represents an active instance of a dashboard in a specific channel."""
    __tablename__ = 'active_dashboards'

    id = Column(Integer, primary_key=True)
    dashboard_configuration_id = Column(Integer, ForeignKey('dashboard_configurations.id', ondelete='CASCADE'), nullable=False, index=True) # Foreign key to the config/template
    guild_id = Column(String(length=30), nullable=False, index=True) # Match migration length
    channel_id = Column(String(length=30), nullable=False, unique=True, index=True) # Match migration length, assuming one active dashboard per channel
    message_id = Column(BIGINT, nullable=True, index=True) # The ID of the Discord message displaying the dashboard
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    error_state = Column(Boolean, default=False, nullable=False, index=True)
    error_message = Column(String, nullable=True) # Use String or Text based on expected length
    config_override = Column(JSONB, nullable=True) # Added to match migration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to the configuration it's based on
    configuration = relationship("DashboardConfigurationEntity", back_populates="active_instances")

    def __repr__(self):
        return f"<ActiveDashboardEntity(id={self.id}, config_id={self.dashboard_configuration_id}, channel_id={self.channel_id}, message_id={self.message_id}, is_active={self.is_active})>"

# Add the back-population to the DashboardConfigurationEntity if it doesn't exist yet
# This requires modifying dashboard_configuration_entity.py
# In DashboardConfigurationEntity:
# active_instances = relationship("ActiveDashboardEntity", back_populates="configuration", cascade="all, delete-orphan") 