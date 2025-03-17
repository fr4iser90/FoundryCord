from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.bot.domain.categories.models.category_model import CategoryModel, CategoryTemplate, CategoryPermission
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.bot.infrastructure.database.models.category_entity import CategoryEntity, CategoryPermissionEntity
from app.shared.infrastructure.database.service import DatabaseService


class CategoryRepositoryImpl(CategoryRepository):
    """Implementation of the Category repository"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def _entity_to_model(self, entity: CategoryEntity) -> CategoryModel:
        """Convert a database entity to a domain model"""
        permissions = []
        for perm_entity in entity.permissions:
            permissions.append(
                CategoryPermission(
                    role_id=perm_entity.role_id,
                    view=perm_entity.view,
                    send_messages=perm_entity.send_messages,
                    manage_messages=perm_entity.manage_messages,
                    manage_channels=perm_entity.manage_channels,
                    manage_category=perm_entity.manage_category
                )
            )
        
        return CategoryModel(
            id=entity.id,
            discord_id=entity.discord_id,
            name=entity.name,
            position=entity.position,
            permission_level=entity.permission_level,
            permissions=permissions,
            is_enabled=entity.is_enabled,
            is_created=entity.is_created,
            metadata=entity.metadata_json or {}  # Use metadata_json here
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
    
    def get_all_categories(self) -> List[CategoryModel]:
        """Get all categories from the database"""
        with self.db_service.session() as session:
            categories = session.query(CategoryEntity).all()
            return [self._entity_to_model(category) for category in categories]
    
    def get_category_by_id(self, category_id: int) -> Optional[CategoryModel]:
        """Get a category by its database ID"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
            return self._entity_to_model(category) if category else None
    
    def get_category_by_discord_id(self, discord_id: int) -> Optional[CategoryModel]:
        """Get a category by its Discord ID"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.discord_id == discord_id).first()
            return self._entity_to_model(category) if category else None
    
    def get_category_by_name(self, name: str) -> Optional[CategoryModel]:
        """Get a category by its name"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.name == name).first()
            return self._entity_to_model(category) if category else None
    
    def save_category(self, category: CategoryModel) -> CategoryModel:
        """Save a category to the database (create or update)"""
        with self.db_service.session() as session:
            entity = self._model_to_entity(category)
            
            if category.id:
                # Update existing
                existing = session.query(CategoryEntity).filter(CategoryEntity.id == category.id).first()
                if existing:
                    # Update fields
                    existing.name = entity.name
                    existing.discord_id = entity.discord_id
                    existing.position = entity.position
                    existing.permission_level = entity.permission_level
                    existing.is_enabled = entity.is_enabled
                    existing.is_created = entity.is_created
                    existing.metadata_json = entity.metadata_json
                    
                    # Handle permissions - delete old ones and add new ones
                    session.query(CategoryPermissionEntity).filter(
                        CategoryPermissionEntity.category_id == existing.id
                    ).delete()
                    
                    for perm in entity.permissions:
                        perm.category_id = existing.id
                        session.add(perm)
                    
                    session.commit()
                    return self._entity_to_model(existing)
            
            # Create new
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return self._entity_to_model(entity)
    
    def update_discord_id(self, category_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a category after it's created in Discord"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
            if category:
                category.discord_id = discord_id
                category.is_created = True
                session.commit()
                return True
            return False
    
    def update_category_status(self, category_id: int, is_created: bool) -> bool:
        """Update the creation status of a category"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
            if category:
                category.is_created = is_created
                session.commit()
                return True
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category from the database"""
        with self.db_service.session() as session:
            category = session.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
            if category:
                session.delete(category)
                session.commit()
                return True
            return False
    
    def create_from_template(self, template: CategoryTemplate) -> CategoryModel:
        """Create a new category from a template"""
        model = template.to_category_model()
        return self.save_category(model)
    
    def get_enabled_categories(self) -> List[CategoryModel]:
        """Get all enabled categories"""
        with self.db_service.session() as session:
            categories = session.query(CategoryEntity).filter(CategoryEntity.is_enabled == True).all()
            return [self._entity_to_model(category) for category in categories]
    
    def create_category(self, category: CategoryModel) -> CategoryModel:
        """Create a new category"""
        with self.db_service.session() as session:
            # Create the category entity
            entity = CategoryEntity(
                discord_id=category.discord_id,
                name=category.name,
                position=category.position,
                permission_level=category.permission_level,
                is_enabled=category.is_enabled,
                is_created=category.is_created,
                metadata_json=category.metadata or {}  # Changed from metadata to metadata_json
            )
            
            session.add(entity)
            session.flush()
            
            # Create the permissions
            for permission in category.permissions:
                perm_entity = CategoryPermissionEntity(
                    category_id=entity.id,
                    role_id=permission.role_id,
                    view=permission.view,
                    send_messages=permission.send_messages,
                    manage_messages=permission.manage_messages,
                    manage_channels=permission.manage_channels,
                    manage_category=permission.manage_category
                )
                session.add(perm_entity)
            
            session.commit()
            
            return self._entity_to_model(entity) 