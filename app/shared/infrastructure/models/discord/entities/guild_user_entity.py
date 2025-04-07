from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class DiscordGuildUserEntity(Base):
    """Discord guild user model - represents a user's role in a specific guild"""
    __tablename__ = 'discord_guild_users'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), ForeignKey('discord_guilds.guild_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('app_users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('app_roles.id'), nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime, server_default=text('now()'), nullable=False)
    
    # Relationships
    user = relationship("AppUserEntity", back_populates="guild_roles")
    role = relationship("AppRoleEntity", back_populates="guild_users")
    guild = relationship("GuildEntity", back_populates="user_roles")
    
    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_guild_user'),
    )
    
    def __repr__(self):
        return f"<DiscordGuildUserEntity(guild_id={self.guild_id}, user_id={self.user_id}, role={self.role.name if self.role else None})>"