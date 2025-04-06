from .system.health_controller import router as health_router
from .dashboard.dashboard_controller import router as dashboard_router
from .guild.guild_config_controller import router as guild_config_router
from .bot.bot_public_controller import router as bot_public_router
from .auth.auth_controller import router as auth_router
from .server.server_selector_controller import router as server_selector_router
from .owner.owner_controller import router as owner_router
from .owner.bot_control_controller import router as owner_bot_control_router

# Liste aller Router in der API v1
routers = [
    auth_router,
    dashboard_router,
    health_router,
    bot_public_router,
    guild_config_router,
    server_selector_router,
    owner_router,
    owner_bot_control_router,
]