"""
Category mapping model for Discord categories.
"""
from sqlalchemy import Column, Integer, String
from app.shared.infrastructure.models.base import Base

class CategoryMapping(Base):
    """Mapping between category types and Discord category IDs"""
    __tablename__ = "category_mappings"
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False)
    category_id = Column(String(20), nullable=False)
    category_name = Column(String(100), nullable=False)
    category_type = Column(String(50), nullable=False)
    
    def __repr__(self):
        return f"<CategoryMapping(id={self.id}, type='{self.category_type}', name='{self.category_name}')>" 