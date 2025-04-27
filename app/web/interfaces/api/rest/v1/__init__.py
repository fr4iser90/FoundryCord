from fastapi import APIRouter
from app.web.interfaces.api.rest.v1.auth import router as auth_router

from app.web.interfaces.api.rest.v1.guild import router as guild_router, general_template_router

from app.web.interfaces.api.rest.v1.owner import (
    router as owner_router, 
    bot_control_router, 
    guild_management_router, 
    bot_logger_router,
    state_snapshot_router
)
from app.web.interfaces.api.rest.v1.system import router as system_router
from app.web.interfaces.api.rest.v1.debug import router as debug_router
# Import generic router from home and rename
from app.web.interfaces.api.rest.v1.home import router as home_router
from app.web.interfaces.api.rest.v1.ui import router as ui_router


# Create main API router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers using their aliased names
router.include_router(auth_router)
#router.include_router(dashboard_router)
router.include_router(guild_router) # Guild-specific routes
router.include_router(general_template_router) # General template routes
router.include_router(owner_router)
router.include_router(bot_control_router)
router.include_router(guild_management_router)
router.include_router(system_router)
router.include_router(debug_router)
router.include_router(home_router) # Use the aliased name
router.include_router(ui_router) # UI routes
router.include_router(bot_logger_router)
router.include_router(state_snapshot_router)

__all__ = ['router']