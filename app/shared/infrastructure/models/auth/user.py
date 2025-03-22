"""
User model for authentication.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class User(Base):
    """User authentication model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    discord_id = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>" 