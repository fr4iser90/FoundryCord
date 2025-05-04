"""
Project model for project management.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class ProjectEntity(Base):
    """Project model for project management"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    guild_id = Column(String(20), nullable=False, index=True)
    owner_id = Column(String(20), nullable=False)  # Discord user ID
    status = Column(String(50), default="active")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    project_data = Column(JSON, nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProjectEntity(id={self.id}, name='{self.name}')>" 