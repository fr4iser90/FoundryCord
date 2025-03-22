from .auth_router import router as auth_router
from .dashboard_router import router as dashboard_router
from .health_router import router as health_router
from .bot_public_router import router as bot_public_router 
from .bot_admin_router import router as bot_admin_router

# Liste aller Router in der API v1
routers = [
    auth_router,
    dashboard_router,
    health_router,
    bot_public_router,
    bot_admin_router
]