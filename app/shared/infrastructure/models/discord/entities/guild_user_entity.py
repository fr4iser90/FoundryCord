from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildUserEntity(Base):
    """Discord guild user model"""
    __tablename__ = 'guild_users'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('app_roles.id'), nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime, server_default=text('now()'), nullable=False)
    
    # Beziehungen
    user = relationship("UserEntity")
    role = relationship("RoleEntity")
    
    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_guild_user'),
    )