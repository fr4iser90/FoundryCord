from fastapi import FastAPI
from app.web.interfaces.web.routers import routers

def register_routers(app: FastAPI):
    """Register all routers with the application"""
    
    # Mount static files first
    from fastapi.staticfiles import StaticFiles
    from pathlib import Path
    
    web_dir = Path(__file__).parent.parent
    static_dir = web_dir / "static"
    
    # Ensure static directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Register all routers
    for router in routers:
        app.include_router(router)