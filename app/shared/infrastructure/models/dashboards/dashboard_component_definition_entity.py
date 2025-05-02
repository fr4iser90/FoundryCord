"""
Model for storing definitions of reusable dashboard components.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.shared.infrastructure.models import Base

class DashboardComponentDefinitionEntity(Base):
    """Dashboard Component Definition model"""
    __tablename__ = "dashboard_component_definitions"

    id = Column(Integer, primary_key=True)
    # Type of dashboard this component belongs to (e.g., 'common', 'welcome', 'monitoring')
    dashboard_type = Column(String(50), nullable=False, index=True)
    # Type of the component itself (e.g., 'button', 'embed', 'view', 'selector', 'modal', 'message')
    component_type = Column(String(50), nullable=False, index=True)
    # Unique key identifying this specific component definition within its type/dashboard_type scope
    component_key = Column(String(100), nullable=False, index=True)
    # JSON blob containing the detailed definition (metadata, config_schema, preview_hints)
    definition = Column(JSON, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Add a unique constraint across dashboard_type and component_key if needed
    # Or maybe component_key should be globally unique?
    # For now, assume key uniqueness is handled by seeding/management logic.
    # UniqueConstraint('dashboard_type', 'component_key', name='uq_dashboard_component_key')

    def __repr__(self):
        return f"<DashboardComponentDefinitionEntity(id={self.id}, type='{self.dashboard_type}', key='{self.component_key}')>" 