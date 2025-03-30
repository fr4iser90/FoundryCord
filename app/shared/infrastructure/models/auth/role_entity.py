"""
Role model for database representation of user app_roles.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class RoleEntity(Base):
    """Database model for app_roles"""
    __tablename__ = "app_roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    users = relationship("GuildUserEntity", back_populates="role")
    
    def __repr__(self):
        return f"<RoleEntity(id={self.id}, name='{self.name}')>"