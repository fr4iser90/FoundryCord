"""
Category mapping model for Discord categories.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.shared.infrastructure.models.base import Base

class CategoryMapping(Base):
    """Mapping between category types and Discord category IDs"""
    __tablename__ = "category_mappings"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False)
    category_id = Column(String(20), nullable=False)
    category_name = Column(String(100), nullable=False)
    category_type = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Behavior flags
    delete_on_shutdown = Column(Boolean, default=False, nullable=False)
    create_on_startup = Column(Boolean, default=True, nullable=False)
    sync_permissions = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<CategoryMapping(id={self.id}, type='{self.category_type}', name='{self.category_name}')>" 