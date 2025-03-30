"""
Content template model for dashboard components.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class ContentTemplateEntity(Base):
    """Content template for dashboard components"""
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("dashboard_components.id", ondelete="CASCADE"), nullable=False)
    template_type = Column(String, nullable=False)  # embed, button, modal
    content = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True)
    
    # Relationships
    component = relationship("DashboardComponentEntity", back_populates="content")
    
    def __repr__(self):
        return f"<ContentTemplateEntity(id={self.id}, type='{self.template_type}')>"
