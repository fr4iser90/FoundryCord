from fastapi import APIRouter
# Import the router from the admin subdirectory
from .admin import users_router as admin_users_router
# Import the router from the designer subdirectory
from .designer import designer_index_router
# TODO: Import landing page router when implemented

# Create a main router for all /guild/{guild_id}/* routes
guild_router = APIRouter()

# Include the admin routes (prefix is already defined)
guild_router.include_router(admin_users_router)
# Include the designer routes (prefix is already defined)
guild_router.include_router(designer_index_router)
# TODO: Include designer sub-routers (categories, channels) if they have different base prefixes
# TODO: Include landing page router

__all__ = [
    'guild_router' # Export the combined guild router
] 