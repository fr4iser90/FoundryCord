from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

class DashboardComponent(Base):
    __tablename__ = "dashboard_components"
    
    id = Column(Integer, primary_key=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    component_type = Column(String, nullable=False)  # button, embed, view, modal, etc.
    component_name = Column(String, nullable=False)
    custom_id = Column(String, nullable=True)
    position = Column(Integer, default=0)  # For ordering components within the dashboard
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # Component-specific configuration
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="components")
    layout = relationship("ComponentLayout", back_populates="component", uselist=False, cascade="all, delete-orphan")
    content = relationship("ContentTemplate", back_populates="component", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardComponent(id={self.id}, type='{self.component_type}', name='{self.component_name}')>"
