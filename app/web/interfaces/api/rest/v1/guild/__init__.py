from fastapi import APIRouter
from .guild_config_controller import GuildConfigController, guild_config_controller
from .guild_selector_controller import GuildSelectorController, guild_selector_controller

# Create a router for the guild module
router = APIRouter()

# Include routes from both controllers
router.include_router(guild_config_controller.router)
router.include_router(guild_selector_controller.router)

__all__ = [
    'GuildConfigController', 
    'GuildSelectorController', 
    'router' # Export the combined router
] 