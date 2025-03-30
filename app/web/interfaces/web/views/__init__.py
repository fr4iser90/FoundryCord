from .admin.admin_view import router as admin_router
from .auth.auth_view import router as auth_router
from .bot.bot_overview_view import router as bot_overview_router
from .bot.bot_control_view import router as bot_control_router
from .bot.bot_stats_view import router as bot_stats_router
from .dashboard.dashboard_view import router as dashboard_router
from .main.main_view import router as main_router

# Liste aller Web-View-Router
routers = [
    main_router,
    admin_router,
    auth_router,
    bot_overview_router,
    bot_control_router,
    bot_stats_router,
    dashboard_router
] 