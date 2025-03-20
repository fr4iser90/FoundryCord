from fastapi import FastAPI

def register_routers(app: FastAPI):
    """Register all application routers"""
    
    # OAuth routes
    from app.web.domain.auth.oauth import router as auth_router
    app.include_router(auth_router)
    
    # API routes
    from app.web.interfaces.api.v1 import routers as api_routers
    for router in api_routers:
        app.include_router(router)
    
    # Web UI routes
    from app.web.interfaces.web import routers as web_routers
    for router in web_routers:
        app.include_router(router)
    
    # Health routes
    from app.web.interfaces.api.v1.health_router import router as health_router
    app.include_router(health_router)