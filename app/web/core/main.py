"""
Main application file for the HomeLab Discord Bot web interface.
"""
import sys
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.web.auth.oauth import router as auth_router
from app.web.api.dashboard import router as dashboard_router
from app.web.auth.dependencies import get_current_user

# Import the bot modules through our bridge module
try:
    from bot_imports import get_bot_interfaces, BOT_IMPORTS_SUCCESS
    bot_interface = get_bot_interfaces()
except ImportError:
    bot_interface = None
    print("Warning: Bot interfaces not available. Some features will be disabled.")

# Create FastAPI application
app = FastAPI(
    title="HomeLab Discord Bot Web Interface",
    description="Web interface for managing the HomeLab Discord Bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router)
app.include_router(dashboard_router)

# Root endpoint - HTML response
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(get_current_user)):
    # If authentication fails, user will be None
    dashboards = []
    if user:
        # In a real implementation, you would fetch dashboards from the database
        dashboards = [
            {"id": 1, "title": "System Overview", "description": "System metrics and status"},
            {"id": 2, "title": "Game Servers", "description": "Game server status and players"}
        ]
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "user": user, "dashboards": dashboards}
    )

# API root endpoint
@app.get("/api")
async def api_root():
    return {
        "message": "HomeLab Discord Bot Web Interface API",
        "bot_interface_available": bot_interface is not None
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot_interface": "available" if bot_interface is not None else "unavailable"
    }

# Debug endpoint to show Python path and available modules
@app.get("/debug")
async def debug():
    return {
        "python_path": sys.path,
        "bot_interface_available": bot_interface is not None,
        "current_directory": os.getcwd(),
        "directory_contents": os.listdir("/app") if os.path.exists("/app") else "Not available",
        "app_directory_exists": os.path.exists("/app/app"),
        "app_bot_directory_exists": os.path.exists("/app/app/bot"),
        "bot_directory_exists": os.path.exists("/app/bot")
    }

# Add error handler for graceful error messages
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    ) 