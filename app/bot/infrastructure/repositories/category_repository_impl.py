from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.bot.domain.categories.models.category_model import CategoryModel, CategoryTemplate, CategoryPermission
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.bot.infrastructure.database.models.category_entity import CategoryEntity, CategoryPermissionEntity
from app.shared.infrastructure.database.service import DatabaseService
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.shared.infrastructure.database.api import get_session

logger = logging.getLogger(__name__)

class CategoryRepositoryImpl(CategoryRepository):
    """Implementation of the CategoryRepository interface"""
    
    def __init__(self, db_service=None):
        """Initialize the repository
        
        Args:
            db_service: Optional database service. If not provided, will use get_session.
        """
        self.db_service = db_service
    
    async def get_all_categories(self) -> List[CategoryModel]:
        """Get all categories from the database"""
        session = await get_session()
        try:
            # Use selectinload to eagerly load permissions
            result = await session.execute(
                select(CategoryEntity).options(selectinload(CategoryEntity.permissions))
            )
            categories = result.scalars().all()
            return [self._entity_to_model(category) for category in categories]
        finally:
            await session.close()
    
    async def get_category_by_name(self, name: str) -> Optional[CategoryModel]:
        """Get a category by its name"""
        session = await get_session()
        try:
            # Use selectinload to eagerly load permissions
            result = await session.execute(
                select(CategoryEntity)
                .options(selectinload(CategoryEntity.permissions))
                .filter(CategoryEntity.name == name)
            )
            category = result.scalars().first()
            if category:
                return self._entity_to_model(category)
            return None
        finally:
            await session.close()
            
    async def get_category_by_id(self, category_id: int) -> Optional[CategoryModel]:
        """Get a category by its database ID"""
        session = await get_session()
        try:
            result = await session.execute(select(CategoryEntity).filter(CategoryEntity.id == category_id))
            category = result.scalars().first()
            if category:
                return self._entity_to_model(category)
            return None
        finally:
            await session.close()
            
    async def get_category_by_discord_id(self, discord_id: int) -> Optional[CategoryModel]:
        """Get a category by its Discord ID"""
        session = await get_session()
        try:
            result = await session.execute(select(CategoryEntity).filter(CategoryEntity.discord_id == discord_id))
            category = result.scalars().first()
            if category:
                return self._entity_to_model(category)
            return None
        finally:
            await session.close()
    
    async def save_category(self, category: CategoryModel) -> CategoryModel:
        """Save a category to the database"""
        session = await get_session()
        try:
            async with session.begin():
                # Convert model to entity
                entity = self._model_to_entity(category)
                
                # Add to session
                session.add(entity)
                await session.flush()
                
                # Update the ID in the model
                category.id = entity.id
                return category
        finally:
            await session.close()
    
    async def update_discord_id(self, category_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a category"""
        session = await get_session()
        try:
            async with session.begin():
                result = await session.execute(select(CategoryEntity).filter(CategoryEntity.id == category_id))
                category = result.scalars().first()
                if category:
                    category.discord_id = discord_id
                    return True
                return False
        finally:
            await session.close()
    
    async def update_category_status(self, category_id: int, is_created: bool) -> bool:
        """Update the creation status of a category"""
        session = await get_session()
        try:
            async with session.begin():
                result = await session.execute(select(CategoryEntity).filter(CategoryEntity.id == category_id))
                category = result.scalars().first()
                if category:
                    category.is_created = is_created
                    return True
                return False
        finally:
            await session.close()
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete a category from the database"""
        session = await get_session()
        try:
            async with session.begin():
                result = await session.execute(select(CategoryEntity).filter(CategoryEntity.id == category_id))
                category = result.scalars().first()
                if category:
                    await session.delete(category)
                    return True
                return False
        finally:
            await session.close()
    
    async def create_from_template(self, template: CategoryTemplate) -> CategoryModel:
        """Create a new category from a template"""
        model = template.to_category_model()
        return await self.save_category(model)
    
    async def get_enabled_categories(self) -> List[CategoryModel]:
        """Get all enabled categories"""
        session = await get_session()
        try:
            # Use selectinload to eagerly load permissions to avoid lazy loading errors
            result = await session.execute(
                select(CategoryEntity)
                .options(selectinload(CategoryEntity.permissions))
                .filter(CategoryEntity.is_enabled == True)
            )
            categories = result.scalars().all()
            return [self._entity_to_model(category) for category in categories]
        finally:
            await session.close()
    
    def _entity_to_model(self, entity: CategoryEntity) -> CategoryModel:
        """Convert a database entity to a domain model"""
        permissions = []
        # Since we're using selectinload, permissions should be eagerly loaded
        if hasattr(entity, 'permissions') and entity.permissions:
            for perm in entity.permissions:
                permissions.append(CategoryPermission(
                    role_id=perm.role_id,
                    view=perm.view,
                    send_messages=perm.send_messages,
                    manage_messages=perm.manage_messages,
                    manage_channels=perm.manage_channels,
                    manage_category=perm.manage_category
                ))
        
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            discord_id=entity.discord_id,
            position=entity.position,
            is_created=entity.is_created,
            is_enabled=entity.is_enabled,
            permissions=permissions,
            metadata=entity.metadata or {}
        )
    
    def _model_to_entity(self, model: CategoryModel) -> CategoryEntity:
        """Convert domain model to database entity"""
        entity = CategoryEntity(
            name=model.name,
            discord_id=model.discord_id,
            position=model.position,
            permission_level=model.permission_level,
            is_enabled=model.is_enabled,
            is_created=model.is_created,
            metadata_json=model.metadata or {}  # Store in metadata_json
        )
        
        if model.id:
            entity.id = model.id
            
        entity.permissions = [
            CategoryPermissionEntity(
                role_id=perm.role_id,
                view=perm.view,
                send_messages=perm.send_messages,
                manage_messages=perm.manage_messages,
                manage_channels=perm.manage_channels,
                manage_category=perm.manage_category
            )
            for perm in model.permissions
        ]
        
        return entity

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        return await get_session() 