"""
Dashboard component model for UI dashboard components.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class DashboardComponentEntity(Base):
    """Dashboard component configuration model"""
    __tablename__ = "dashboard_components"
    
    id = Column(Integer, primary_key=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True)
    component_type = Column(String(50), nullable=False, index=True)  # button, embed, modal, selector, view
    component_name = Column(String(100), nullable=False)
    custom_id = Column(String(100), nullable=True)
    position = Column(Integer, default=0)  # For ordering
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("DashboardEntity", back_populates="components")
    layout = relationship("ComponentLayoutEntity", back_populates="component", uselist=False, cascade="all, delete-orphan")
    content = relationship("ContentTemplateEntity", back_populates="component", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardComponentEntity(id={self.id}, type='{self.component_type}', name='{self.component_name}')>"
