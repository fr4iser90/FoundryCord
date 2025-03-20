from fastapi import FastAPI
from app.web.interfaces.web.routers import routers
from app.web.api.dashboard import router as dashboard_api_router
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

def register_routers(app: FastAPI):
    """Register all routers with the application"""
    
    # Register all routers
    for router in routers:
        app.include_router(router)
        logger.debug(f"Registered router: {router}")
    
    # Register API routers
    app.include_router(dashboard_api_router)