from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="planning")
    priority = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    created_by = Column(String, ForeignKey('users.discord_id'), nullable=True)
    
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Project(name='{self.name}', status='{self.status}')>"

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(title='{self.title}', status='{self.status}')>"
