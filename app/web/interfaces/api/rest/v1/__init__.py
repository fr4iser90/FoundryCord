from fastapi import APIRouter
from app.web.interfaces.api.rest.v1.auth import router as auth_router
from app.web.interfaces.api.rest.v1.dashboard import router as dashboard_router
from app.web.interfaces.api.rest.v1.guild import router as guild_router
from app.web.interfaces.api.rest.v1.owner import router as owner_router, bot_control_router, server_management_router
from app.web.interfaces.api.rest.v1.server import router as server_router
from app.web.interfaces.api.rest.v1.system import router as system_router
from app.web.interfaces.api.rest.v1.debug import router as debug_router
from app.web.interfaces.api.rest.v1.home import home_overview_router

# Create main API router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(guild_router)
router.include_router(owner_router)
router.include_router(bot_control_router)
router.include_router(server_management_router)
router.include_router(server_router)
router.include_router(system_router)
router.include_router(debug_router)
router.include_router(home_overview_router)

__all__ = ['router']