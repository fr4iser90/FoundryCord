"""
Content template model for dashboard components.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..base import Base

class ContentTemplate(Base):
    """Content template for dashboard components"""
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("dashboard_components.id", ondelete="CASCADE"), nullable=False)
    template_type = Column(String, nullable=False)  # embed, button, modal
    content = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True)
    
    # Relationships
    component = relationship("DashboardComponent", back_populates="content")
    
    def __repr__(self):
        return f"<ContentTemplate(id={self.id}, type='{self.template_type}')>"
