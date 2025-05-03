"""SQLAlchemy model for active dashboard instances."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class ActiveDashboardEntity(Base):
    """Represents an active instance of a dashboard in a specific channel."""
    __tablename__ = 'active_dashboards'

    id = Column(Integer, primary_key=True)
    dashboard_configuration_id = Column(Integer, ForeignKey('dashboard_configurations.id'), nullable=False, index=True) # Foreign key to the config/template
    guild_id = Column(String, nullable=False, index=True)
    channel_id = Column(String, nullable=False, unique=True, index=True) # Assuming one active dashboard per channel
    message_id = Column(String, nullable=True) # The ID of the Discord message displaying the dashboard
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to the configuration it's based on
    configuration = relationship("DashboardConfigurationEntity", back_populates="active_instances")

    def __repr__(self):
        return f"<ActiveDashboardEntity(id={self.id}, config_id={self.dashboard_configuration_id}, channel_id={self.channel_id}, message_id={self.message_id}, is_active={self.is_active})>"

# Add the back-population to the DashboardConfigurationEntity if it doesn't exist yet
# This requires modifying dashboard_configuration_entity.py
# In DashboardConfigurationEntity:
# active_instances = relationship("ActiveDashboardEntity", back_populates="configuration", cascade="all, delete-orphan") 