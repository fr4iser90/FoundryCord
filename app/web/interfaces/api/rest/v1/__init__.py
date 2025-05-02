from fastapi import APIRouter
from app.web.interfaces.api.rest.v1.auth import router as auth_router
from app.web.interfaces.api.rest.v1.guild import router as guild_router
from app.web.interfaces.api.rest.v1.dashboards import router as dashboard_router
# Import only the aggregated router from owner
from app.web.interfaces.api.rest.v1.owner import router as owner_router
from app.web.interfaces.api.rest.v1.system import router as system_router
from app.web.interfaces.api.rest.v1.debug import router as debug_router
from app.web.interfaces.api.rest.v1.home import router as home_router
from app.web.interfaces.api.rest.v1.ui import router as ui_router


router = APIRouter(prefix="/api/v1")

# Include all aggregated routers
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(guild_router)
router.include_router(owner_router) # Include the single owner router
router.include_router(system_router)
router.include_router(debug_router)
router.include_router(home_router)
router.include_router(ui_router)

__all__ = ['router']