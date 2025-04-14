from .auth.auth_view import router as auth_router
from .home.overview import router as home_router
from .main.main_view import router as main_router
from .navbar.server_selector_view import router as server_selector_router
from .debug.debug_view import router as debug_router
from .guild import guild_router
from .owner.owner_view import router as owner_router
from .owner.bot_control_view import router as bot_control_router
from .owner.bot_logger_view import router as bot_logger_router
# Liste aller Web-View-Router
routers = [
    main_router,
    auth_router,
    home_router,
    server_selector_router,
    debug_router,   
    guild_router,
    owner_router,
    bot_control_router,
    bot_logger_router
] 