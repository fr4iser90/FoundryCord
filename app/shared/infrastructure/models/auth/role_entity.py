"""
Role model for database representation of user app_roles.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class AppRoleEntity(Base):
    """Database model for app_roles"""
    __tablename__ = "app_roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    permissions = Column(String(255), nullable=True)  # Comma-separated list of permissions
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    guild_users = relationship("DiscordGuildUserEntity", back_populates="role")
    
    def __repr__(self):
        return f"<AppRoleEntity(id={self.id}, name='{self.name}', permissions='{self.permissions}')>"