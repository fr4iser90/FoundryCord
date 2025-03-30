"""
User model for authentication.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class AppUserEntity(Base):
    """User authentication model"""
    __tablename__ = "app_users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    discord_id = Column(String(255), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('app_roles.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    sessions = relationship("SessionEntity", back_populates="user", cascade="all, delete")
    
    def __repr__(self):
        return f"<AppUserEntity(id={self.id}, username='{self.username}', discord_id='{self.discord_id}')>" 