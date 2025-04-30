from fastapi import APIRouter
from .admin.guild_config_controller import GuildConfigController, guild_config_controller
from .selector.guild_selector_controller import GuildSelectorController, guild_selector_controller
# Import the new template controller
from .designer.guild_template_controller import GuildTemplateController, guild_template_controller
# Import the user management router
from .admin.guild_user_management_controller import guild_user_management_router

# Create a router for the guild module
router = APIRouter()

# Include routes from all guild-related controllers
router.include_router(guild_config_controller.router)
router.include_router(guild_selector_controller.router)
router.include_router(guild_user_management_router) # Use the router instance directly
router.include_router(guild_template_controller.router) # Add the guild-specific template router


__all__ = [
    'GuildConfigController', 
    'GuildSelectorController', 
    'GuildTemplateController', # Add the new controller name
    'guild_user_management_router', # Export the router instance
    'router', # Export the combined guild router
] 