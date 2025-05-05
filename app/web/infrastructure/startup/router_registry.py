from fastapi import FastAPI
from app.web.interfaces.web import web_router  # Neuer Import für die Web-Views
from app.web.interfaces.api import api_router  # Behalten wir für API-Routen
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

def register_routers(app: FastAPI):
    """Register all routers with the application"""
    
    # Register the consolidated web router (contains all views)
    app.include_router(web_router)
    logger.debug(f"Registered web router: {web_router}")
    
    
    # Register the main API router which includes all v1 routes
    app.include_router(api_router)
    logger.debug(f"Registered API router: {api_router}")