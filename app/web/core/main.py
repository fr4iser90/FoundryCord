"""
Main application file for the HomeLab Discord Bot web interface.
"""
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pathlib

# Import app components
from app.web.domain.auth import auth_router
from app.web.interfaces.api.v1 import routers as api_routers
from app.web.interfaces.web import routers as web_routers
from app.web.domain.auth.dependencies import get_current_user
from app.web.interfaces.api.v1.health_routes import router as health_router

# Import the bot modules through our bridge module
# try:
#     from app.web.infrastructure.setup.bot_imports import get_bot_interfaces, BOT_IMPORTS_SUCCESS
#     bot_interface = get_bot_interfaces()
# except ImportError:
#     bot_interface = None
#     print("Warning: Bot interfaces not available. Some features will be disabled.")

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

# Get the absolute path to the templates directory
base_dir = pathlib.Path(__file__).parent
templates_dir = os.path.join(base_dir, "templates")
print(f"Templates directory: {templates_dir}")
templates = Jinja2Templates(directory=templates_dir)

# Initialize static files
static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth_router)

# Include API routers
for router in api_routers:
    app.include_router(router)

# Include Web routers
for router in web_routers:
    app.include_router(router)

# Include health router
app.include_router(health_router)

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
        "bot_directory_exists": os.path.exists("/app/bot"),
        "templates_dir": templates_dir,
        "templates_exists": os.path.exists(templates_dir),
        "index_exists": os.path.exists(os.path.join(templates_dir, "index.html"))
    }

# Add error handler for graceful error messages
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)