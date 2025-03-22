from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import CategoryMapping
from typing import Optional, List

class CategoryRepositoryImpl:
    def __init__(self, session: AsyncSession = None):
        self.session = session
    
    async def get_by_id(self, category_id: int) -> Optional[CategoryMapping]:
        """Get a category by its database ID"""
        result = await self.session.execute(select(CategoryMapping).where(CategoryMapping.id == category_id))
        return result.scalar_one_or_none()
    
    async def get_by_discord_id(self, category_discord_id: str) -> Optional[CategoryMapping]:
        """Get a category by its Discord category ID"""
        result = await self.session.execute(select(CategoryMapping).where(CategoryMapping.category_id == category_discord_id))
        return result.scalar_one_or_none()
    
    async def get_by_guild_and_type(self, guild_id: str, category_type: str) -> Optional[CategoryMapping]:
        """Get a category by guild ID and category type"""
        result = await self.session.execute(
            select(CategoryMapping).where(
                CategoryMapping.guild_id == guild_id,
                CategoryMapping.category_type == category_type
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(self, category_type: str) -> Optional[CategoryMapping]:
        """Get a category by type (returns first matching category)"""
        result = await self.session.execute(
            select(CategoryMapping).where(CategoryMapping.category_type == category_type)
        )
        return result.scalar_one_or_none()
    
    async def get_by_guild(self, guild_id: str) -> List[CategoryMapping]:
        """Get all categories for a specific guild"""
        result = await self.session.execute(
            select(CategoryMapping).where(CategoryMapping.guild_id == guild_id)
        )
        return result.scalars().all()
    
    async def get_all(self) -> List[CategoryMapping]:
        """Get all category mappings"""
        result = await self.session.execute(select(CategoryMapping))
        return result.scalars().all()
    
    async def create(self, guild_id: str, category_id: str, category_name: str, category_type: str = "homelab") -> CategoryMapping:
        """Create a new category mapping"""
        category = CategoryMapping(
            guild_id=guild_id,
            category_id=category_id,
            category_name=category_name,
            category_type=category_type
        )
        self.session.add(category)
        await self.session.commit()
        return category
    
    async def update(self, category: CategoryMapping) -> CategoryMapping:
        """Update an existing category mapping"""
        self.session.add(category)
        await self.session.commit()
        return category
    
    async def delete(self, category: CategoryMapping) -> None:
        """Delete a category mapping"""
        await self.session.delete(category)
        await self.session.commit()
    
    async def save_or_update(self, guild_id: str, category_id: str, category_name: str, category_type: str) -> CategoryMapping:
        """Save a new category or update existing one"""
        existing = await self.get_by_guild_and_type(guild_id, category_type)
        
        if existing:
            existing.category_id = category_id
            existing.category_name = category_name
            return await self.update(existing)
        else:
            return await self.create(guild_id, category_id, category_name, category_type)