from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class ProjectMember(Base):
    """Model for project members"""
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    joined_at = Column(DateTime, default=func.now())
    
    # Relationship
    project = relationship("Project", back_populates="members")
    
    def __repr__(self):
        return f"<ProjectMember project_id={self.project_id}, user_id={self.user_id}>" 