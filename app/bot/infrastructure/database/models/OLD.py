from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(String, unique=True)
    username = Column(String)
    role = Column(String)  # super_admin, admin, moderator, user, guest
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    token = Column(String) 
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    command_type = Column(String)
    attempt_count = Column(BigInteger, default=0)
    last_attempt = Column(DateTime)
    blocked_until = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    action = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ChannelMapping(Base):
    __tablename__ = 'channel_mappings'
    
    id = Column(Integer, primary_key=True)
    channel_name = Column(String, nullable=False)
    channel_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

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

class DashboardMessage(Base):
    __tablename__ = "dashboard_messages"
    
    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String, unique=True, index=True)
    message_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DashboardMessage(dashboard_type='{self.dashboard_type}', message_id={self.message_id})>"

class CategoryMapping(Base):
    __tablename__ = 'category_mappings'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String, unique=True, index=True)
    category_id = Column(String)
    category_name = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CategoryMapping(guild={self.guild_id}, category={self.category_id})>"