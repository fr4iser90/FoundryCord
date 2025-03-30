from fastapi import FastAPI
from app.web.interfaces.web import web_router  # Neuer Import für die Web-Views
#from app.web.api.dashboard import router as dashboard_api_router
from app.web.interfaces.api import api_router  # Behalten wir für API-Routen
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

def register_routers(app: FastAPI):
    """Register all routers with the application"""
    
    # Register the consolidated web router (contains all views)
    app.include_router(web_router)
    logger.debug(f"Registered web router: {web_router}")
    
    # Register API routers
    #app.include_router(dashboard_api_router)
    
    # Register the main API router which includes all v1 routes
    app.include_router(api_router)
    logger.debug(f"Registered API router: {api_router}")