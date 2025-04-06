from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base
from app.shared.infrastructure.models.discord.enums.category import CategoryPermissionLevel

class CategoryEntity(Base):
    """Database entity for Discord categories"""
    __tablename__ = "discord_categories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, nullable=True, unique=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    permission_level = Column(Enum(CategoryPermissionLevel), nullable=False, default=CategoryPermissionLevel.PUBLIC)
    is_enabled = Column(Boolean, nullable=False, default=True)
    is_created = Column(Boolean, nullable=False, default=False)
    metadata_json = Column(JSON, nullable=True)
    
    # Relationships
    permissions = relationship("CategoryPermissionEntity", back_populates="category", cascade="all, delete-orphan")
    # Use string reference to avoid circular import
    channels = relationship("ChannelEntity", back_populates="category")


class CategoryPermissionEntity(Base):
    """Database entity for category permissions"""
    __tablename__ = "discord_category_permissions"
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("discord_categories.id"), nullable=False)
    role_id = Column(Integer, nullable=False)
    view = Column(Boolean, nullable=False, default=False)
    send_messages = Column(Boolean, nullable=False, default=False)
    manage_messages = Column(Boolean, nullable=False, default=False)
    manage_channels = Column(Boolean, nullable=False, default=False)
    manage_category = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    category = relationship("CategoryEntity", back_populates="permissions") 