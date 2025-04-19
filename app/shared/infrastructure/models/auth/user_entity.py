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
    is_owner = Column(Boolean, default=False)  # Global OWNER flag
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    avatar = Column(String(255), nullable=True)  # URL zum Avatar-Bild
    last_selected_guild_id = Column(String(20), nullable=True) # Store the last selected guild ID
    
    # Relationships
    sessions = relationship("SessionEntity", back_populates="user", cascade="all, delete")
    guild_roles = relationship("DiscordGuildUserEntity", back_populates="user", cascade="all, delete")
    
    def __repr__(self):
        return f"<AppUserEntity(id={self.id}, username='{self.username}', is_owner={self.is_owner})>" 