from .system.health_controller import router as health_router
from .dashboard.dashboard_controller import router as dashboard_router
from .guild.guild_config_controller import router as guild_config_router
from .bot.bot_admin_controller import router as bot_admin_router
from .bot.bot_public_controller import router as bot_public_router
from .auth.auth_controller import router as auth_router

# Liste aller Router in der API v1
routers = [
    auth_router,
    dashboard_router,
    health_router,
    bot_public_router,
    bot_admin_router,
    guild_config_router
]