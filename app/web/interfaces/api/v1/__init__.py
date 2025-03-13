from .dashboard import router as dashboard_router
from .auth import router as auth_router

routers = [
    dashboard_router,
    auth_router
]
