from fastapi import APIRouter
from .admin.guild_config_controller import guild_config_controller
from .selector.guild_selector_controller import guild_selector_controller
# Import the aggregated router from the designer subdirectory
from .designer import router as designer_router
# Import the user management router
from .admin.guild_user_management_controller import guild_user_management_router

# Create a router for the guild module
router = APIRouter()

# Include routes from all guild-related controllers/submodules
router.include_router(guild_config_controller.router)
router.include_router(guild_selector_controller.router)
router.include_router(guild_user_management_router)
# Include the aggregated designer router
router.include_router(designer_router)

# Define the public interface for this module
__all__ = ['router'] 