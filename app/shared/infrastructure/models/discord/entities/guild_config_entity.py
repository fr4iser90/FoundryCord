from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base

class GuildConfigEntity(Base):
    """Configuration for a Discord guild/server"""
    __tablename__ = "guild_configs"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), ForeignKey('discord_guilds.guild_id', ondelete='CASCADE'), unique=True, nullable=False)
    guild_name = Column(String(255), nullable=False)
    
    # Feature flags (Categories/Channels removed, others kept for functional toggle)
    # enable_categories = Column(Boolean, default=True)
    # enable_channels = Column(Boolean, default=True)
    enable_dashboard = Column(Boolean, default=False)
    enable_tasks = Column(Boolean, default=False)
    enable_services = Column(Boolean, default=False)
    
    # Settings
    settings = Column(String)  # JSON formatted string for additional settings
    
    # --- Active Template --- 
    active_template_id = Column(Integer, ForeignKey('guild_templates.id', ondelete='SET NULL'), nullable=True)
    
    # Relationship back to guild
    guild = relationship("GuildEntity", back_populates="config", uselist=False)
    
    # Relationship to the active template
    active_template = relationship("GuildTemplateEntity", foreign_keys=[active_template_id])
    
    def __repr__(self):
        return f"<GuildConfigEntity(guild_id='{self.guild_id}', name='{self.guild_name}')>"