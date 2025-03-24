"""
Component layout model for dashboard positioning.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..base import Base

class ComponentLayoutEntity(Base):
    """Layout information for dashboard components"""
    __tablename__ = "component_layouts"
    
    # Add extend_existing=True to prevent errors if table is redefined
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("dashboard_components.id", ondelete="CASCADE"), nullable=False)
    row_position = Column(Integer, default=0)  # Renamed from 'row' to avoid SQL reserved word
    col_position = Column(Integer, default=0)  # Renamed from 'column' to avoid SQL reserved word
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    style = Column(String, nullable=True)  # CSS or display style information
    additional_props = Column(JSON, nullable=True)  # For flexible styling options
    
    # Relationships
    component = relationship("DashboardComponentEntity", back_populates="layout")
    
    def __repr__(self):
        return f"<ComponentLayoutEntity(id={self.id}, row={self.row_position}, col={self.col_position})>"
