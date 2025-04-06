from typing import Optional, List, Dict
import discord
from app.shared.infrastructure.models.discord.entities.category_entity import CategoryEntity
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
import logging

logger = logging.getLogger("homelab.bot")

class CategoryBuilder:
    """Service for building Discord categories from database models"""
    
    def __init__(self, category_repository: CategoryRepository):
        """Initialize the category builder with a repository"""
        self.category_repository = category_repository
    
    async def create_category(
        self, guild: discord.Guild, 
        name: str, 
        position: int = 0, 
        permissions: List[Dict] = None
    ) -> Optional[discord.CategoryChannel]:
        """Create a new category in the guild"""
        logger.info(f"Creating category {name} at position {position}")
        
        # Create category with optional permissions
        try:
            overwrites = {}
            if permissions:
                for perm in permissions:
                    role = discord.utils.get(guild.app_roles, id=perm.get('role_id'))
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=perm.get('view', False),
                            send_messages=perm.get('send_messages', False),
                            manage_messages=perm.get('manage_messages', False),
                            manage_channels=perm.get('manage_channels', False)
                        )
            
            category = await guild.create_category(
                name=name,
                position=position,
                overwrites=overwrites
            )
            
            logger.info(f"Created category: {name} with ID {category.id}")
            return category
            
        except discord.Forbidden:
            logger.error(f"Bot does not have permission to create category: {name}")
            return None
        except discord.HTTPException as e:
            logger.error(f"Failed to create category {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating category {name}: {e}")
            return None
    
    async def setup_all_categories(self, guild: discord.Guild) -> List[discord.CategoryChannel]:
        """Set up all enabled categories from the database"""
        categories = self.category_repository.get_enabled_categories()
        created_categories = []
        
        # Sort categories by position
        categories.sort(key=lambda c: c.position)
        
        for category in categories:
            # Skip if category is already created in Discord
            if category.discord_id:
                existing = discord.utils.get(guild.categories, id=category.discord_id)
                if existing:
                    created_categories.append(existing)
                    continue
            
            # Create the category
            discord_category = await self.create_category(guild, category.name, category.position, category.permissions)
            if discord_category:
                created_categories.append(discord_category)
        
        return created_categories
    
    async def sync_categories(self, guild: discord.Guild) -> None:
        """Sync database categories with existing Discord categories"""
        for discord_category in guild.categories:
            # Check if category exists in database
            category = self.category_repository.get_category_by_discord_id(discord_category.id)
            if not category:
                # Find by name
                category = self.category_repository.get_category_by_name(discord_category.name)
                if category:
                    # Update Discord ID
                    self.category_repository.update_discord_id(category.id, discord_category.id)
                    print(f"Linked existing category: {discord_category.name} (ID: {discord_category.id})") 