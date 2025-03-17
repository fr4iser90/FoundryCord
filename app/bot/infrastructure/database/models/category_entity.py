from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.infrastructure.database.models.base import Base
from app.bot.domain.categories.models.category_model import CategoryPermissionLevel


class CategoryEntity(Base):
    """Database entity for Discord categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, nullable=True, unique=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    permission_level = Column(Enum(CategoryPermissionLevel), nullable=False, default=CategoryPermissionLevel.PUBLIC)
    is_enabled = Column(Boolean, nullable=False, default=True)
    is_created = Column(Boolean, nullable=False, default=False)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    permissions = relationship("CategoryPermissionEntity", back_populates="category", cascade="all, delete-orphan")
    channels = relationship("ChannelEntity", back_populates="category", cascade="all, delete-orphan")


class CategoryPermissionEntity(Base):
    """Database entity for category permissions"""
    __tablename__ = "category_permissions"
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    role_id = Column(Integer, nullable=False)
    view = Column(Boolean, nullable=False, default=False)
    send_messages = Column(Boolean, nullable=False, default=False)
    manage_messages = Column(Boolean, nullable=False, default=False)
    manage_channels = Column(Boolean, nullable=False, default=False)
    manage_category = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    category = relationship("CategoryEntity", back_populates="permissions") 