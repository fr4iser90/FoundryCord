from fastapi import APIRouter
# Import the router from the admin subdirectory
from .admin import users_router as admin_users_router
# TODO: Import designer router when implemented

# Create a main router for all /guild/{guild_id}/* routes
guild_router = APIRouter()

# Include the admin routes (prefix is already defined in admin_users_router)
guild_router.include_router(admin_users_router)
# TODO: Include designer routes when implemented
# guild_router.include_router(designer_router)

__all__ = [
    'guild_router' # Export the combined guild router
] 