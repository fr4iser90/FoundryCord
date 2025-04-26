from .auth.auth_view import router as auth_router
from .home.overview import router as home_router
from .main.main_view import router as main_router
from .navbar.server_selector_view import router as server_selector_router
from .debug.debug_view import router as debug_router
from .guild import guild_router
from .owner.control_view import router as owner_control_router       
from .owner.bot_logger_view import router as owner_bot_logger_router
from .owner.features_view import router as owner_features_router     
from .owner.server_management_view import router as owner_server_management_router 
from .owner.state_monitor_view import router as owner_state_monitor_router

# Liste aller Web-View-Router
routers = [
    main_router,
    auth_router,
    home_router,
    server_selector_router,
    debug_router,   
    guild_router,
    owner_control_router,
    owner_bot_logger_router,
    owner_features_router,
    owner_server_management_router,
    owner_state_monitor_router 
] 