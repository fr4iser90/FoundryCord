from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..base import Base

class ComponentLayout(Base):
    __tablename__ = "component_layouts"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("dashboard_components.id", ondelete="CASCADE"), nullable=False)
    row = Column(Integer, default=0)
    column = Column(Integer, default=0)
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    style = Column(String, nullable=True)  # CSS or display style information
    additional_props = Column(JSON, nullable=True)  # For flexible styling options
    
    # Relationships
    component = relationship("DashboardComponent", back_populates="layout")
    
    def __repr__(self):
        return f"<ComponentLayout(id={self.id}, row={self.row}, column={self.column})>"
