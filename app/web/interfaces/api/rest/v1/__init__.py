from fastapi import APIRouter
from app.web.interfaces.api.rest.v1.auth import auth_router
from app.web.interfaces.api.rest.v1.bot import bot_public_router
from app.web.interfaces.api.rest.v1.dashboard import dashboard_router
from app.web.interfaces.api.rest.v1.guild import guild_config_router
from app.web.interfaces.api.rest.v1.owner import (
    owner_router, 
    bot_control_router,
    server_management_router
)
from app.web.interfaces.api.rest.v1.server import server_selector_router
from app.web.interfaces.api.rest.v1.system import health_router
from app.web.interfaces.api.rest.v1.debug import debug_controller
from app.web.interfaces.api.rest.v1.guild.users import guild_user_management_controller

# Create main API router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers
router.include_router(auth_router)
router.include_router(bot_public_router)
router.include_router(dashboard_router)
router.include_router(guild_config_router)
router.include_router(owner_router)
router.include_router(bot_control_router)
router.include_router(server_management_router)
router.include_router(server_selector_router)
router.include_router(health_router)
router.include_router(debug_controller.router)
router.include_router(guild_user_management_controller.router)

# Export routers for easy access
routers = [router]

__all__ = ['router', 'routers']