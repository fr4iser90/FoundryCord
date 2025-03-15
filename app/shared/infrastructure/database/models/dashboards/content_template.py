from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..base import Base

class ContentTemplate(Base):
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("dashboard_components.id", ondelete="CASCADE"), nullable=False)
    template_type = Column(String, nullable=False)  # text, embed, button, etc.
    locale = Column(String, default="en-US")  # For internationalization
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # The actual template content
    variables = Column(JSON, nullable=True)  # Variables that can be replaced in the template
    
    # Relationships
    component = relationship("DashboardComponent", back_populates="content")
    
    def __repr__(self):
        return f"<ContentTemplate(id={self.id}, type='{self.template_type}', locale='{self.locale}')>"
