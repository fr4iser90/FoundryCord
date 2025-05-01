from typing import Optional, List, Dict
import nextcord
from app.shared.infrastructure.models.discord.entities.category_entity import CategoryEntity
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
import logging
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger("homelab.bot")

class CategoryBuilder:
    """Service for building Discord categories from database models"""
    
    def __init__(self):
        """Initialize the category builder"""
        pass
    
    async def create_category(
        self, guild: nextcord.Guild, 
        category_model: CategoryEntity,
        session: AsyncSession
    ) -> Optional[nextcord.CategoryChannel]:
        """Create a new category in the guild from a model"""
        name = category_model.name
        position = category_model.position
        # Permissions need to be handled based on the model's relation
        # Placeholder: Assume permissions are not directly passed anymore, 
        # but accessed via the model if needed after creation or configured separately.
        permissions_data = [] # category_model.permissions should be accessed if needed
        
        logger.info(f"Creating category {name} at position {position}")
        
        # Instantiate repo if needed
        category_repo = CategoryRepositoryImpl(session)

        # Create category with optional permissions
        try:
            overwrites = {}
            await session.refresh(category_model, ['permissions'])
            if hasattr(category_model, 'permissions') and category_model.permissions:
                for perm in category_model.permissions:
                    # Ensure role ID exists
                    if perm.role_id is None:
                        logger.warning(f"Skipping permission for category {name}: role_id is None")
                        continue
                        
                    role = guild.get_role(perm.role_id)
                    if role:
                        # Use getattr to safely access permission attributes
                        overwrites[role] = nextcord.PermissionOverwrite(
                            view_channel=getattr(perm, 'view_channel', None),
                            send_messages=getattr(perm, 'send_messages', None),
                            manage_messages=getattr(perm, 'manage_messages', None),
                            manage_channels=getattr(perm, 'manage_channel', None)
                            # Add other permissions as needed from CategoryPermissionEntity
                        )
                    else:
                        logger.warning(f"Role with ID {perm.role_id} not found in guild {guild.name} for category {name}")
            
            category = await guild.create_category(
                name=name,
                position=position,
                overwrites=overwrites
            )
            
            logger.info(f"Created category: {name} with ID {category.id}")
            
            # Update DB with Discord ID using repo
            await category_repo.update_discord_id(category_model.id, category.id)
            return category
            
        except nextcord.Forbidden:
            logger.error(f"Bot does not have permission to create category: {name}")
            return None
        except nextcord.HTTPException as e:
            logger.error(f"Failed to create category {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating category {name}: {e}")
            return None 