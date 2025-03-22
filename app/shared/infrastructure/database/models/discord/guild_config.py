from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.infrastructure.database.models.base import Base

class GuildConfig(Base):
    """Configuration for a Discord guild/server"""
    __tablename__ = "guild_configs"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String, unique=True, nullable=False)
    guild_name = Column(String, nullable=False)
    
    # Feature flags
    enable_categories = Column(Boolean, default=True)
    enable_channels = Column(Boolean, default=True)
    enable_dashboard = Column(Boolean, default=False)
    enable_tasks = Column(Boolean, default=False)
    enable_services = Column(Boolean, default=False)
    
    # Settings
    settings = Column(String)  # JSON formatted string for additional settings