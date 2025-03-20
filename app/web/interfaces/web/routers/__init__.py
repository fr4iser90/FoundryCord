from .main_router import router as main_router
from .auth_router import router as auth_router
from .dashboard_router import router as dashboard_router
from .admin_router import router as admin_router
from .bot_router import router as bot_router

# Export all routers for use in the web interface
routers = [
    main_router,
    auth_router,
    dashboard_router,
    admin_router,
    bot_router
]
