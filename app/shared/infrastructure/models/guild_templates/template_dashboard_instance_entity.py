"""
SQLAlchemy model for dashboard instances defined within guild templates.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.infrastructure.models import Base # Assuming Base is defined here

# TODO: Rename class to DashboardConfigurationEntity?
class TemplateDashboardInstanceEntity(Base):
    """Represents a dashboard configuration (formerly instance linked to channel)."""
    __tablename__ = "dashboard_instances"

    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String(100), nullable=False, comment="Functional type like 'welcome', 'project', 'gamehub'") # Clarified comment
    name = Column(String(100), nullable=False, comment="User-defined name for this configuration") # Clarified comment
    description = Column(String(500), nullable=True) # Added description field
    config = Column(JSON, nullable=True, comment="JSON configuration defining the dashboard structure and components") # Clarified comment
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


    def __repr__(self):
        # Removed channel_template_id from repr
        return f"<TemplateDashboardInstanceEntity(id={self.id}, name='{self.name}', type='{self.dashboard_type}')>" 