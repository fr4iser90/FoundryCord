"""
Database entity models package.
Import all models here to avoid circular imports.
"""

# Import all entity models so they are loaded in the correct order
from app.bot.infrastructure.database.models.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.bot.infrastructure.database.models.category_entity import CategoryEntity, CategoryPermissionEntity

__all__ = [
    'ChannelEntity',
    'ChannelPermissionEntity',
    'CategoryEntity',
    'CategoryPermissionEntity',
] 