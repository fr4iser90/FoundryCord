from .dashboard_router import router as dashboard_router
from .health_router import router as health_router
from .bot.bot_admin_controller import router as bot_admin_router
from .bot.bot_public_controller import router as bot_public_router
from .auth.auth_controller import router as auth_router

# Liste aller Router in der API v1
routers = [
    auth_router,
    dashboard_router,
    health_router,
    bot_public_router,
    bot_admin_router
]