from typing import Optional, List
import discord
from app.bot.domain.categories.models.category_model import CategoryModel
from app.bot.domain.categories.repositories.category_repository import CategoryRepository


class CategoryBuilder:
    """Service for building Discord categories from database models"""
    
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
    
    async def create_category(self, guild: discord.Guild, category: CategoryModel) -> Optional[discord.CategoryChannel]:
        """Create a Discord category from a category model"""
        if not category.is_valid:
            print(f"Invalid category configuration: {category.name}")
            return None
        
        # Create category overwrites for permissions
        overwrites = {}
        for permission in category.permissions:
            role = guild.get_role(permission.role_id)
            if role:
                overwrite = discord.PermissionOverwrite()
                overwrite.view_channel = permission.view
                overwrite.send_messages = permission.send_messages
                overwrite.manage_messages = permission.manage_messages
                overwrite.manage_channels = permission.manage_channels
                overwrites[role] = overwrite
        
        try:
            # Create the category in Discord
            discord_category = await guild.create_category(
                name=category.name,
                overwrites=overwrites,
                position=category.position
            )
            
            # Update the category in the database with the Discord ID
            self.category_repository.update_discord_id(category.id, discord_category.id)
            
            print(f"Created category: {category.name} (ID: {discord_category.id})")
            return discord_category
        
        except discord.Forbidden:
            print(f"Bot lacks permissions to create category: {category.name}")
            return None
        except discord.HTTPException as e:
            print(f"Failed to create category {category.name}: {str(e)}")
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
            discord_category = await self.create_category(guild, category)
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