from .dashboard_router import router as dashboard_router
from .auth_router import router as auth_router
from .health_router import router as health_router

routers = [
    dashboard_router,
    auth_router,
    health_router
]
