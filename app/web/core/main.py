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
from app.web.infrastructure.security.auth import get_current_user
from app.web.core.middleware import role_check_middleware

from app.web.core.router_registry import register_routers

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

# Add custom role middleware
app.middleware("http")(role_check_middleware)

# Get the absolute path to the templates directory
base_dir = pathlib.Path(__file__).parent.parent
templates_dir = os.path.join(base_dir, "templates")
print(f"Templates directory: {templates_dir}")
templates = Jinja2Templates(directory=templates_dir)

# Initialize static files
static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

register_routers(app)


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

# Add bot_interface variable initialization
bot_interface = None

# Add the missing start_web_server function
def start_web_server(dependency_container):
    """
    Start the web server with the provided dependency container.
    
    Args:
        dependency_container: The dependency container with all required services
    """
    global bot_interface
    
    # Extract necessary dependencies from the container
    try:
        # Get bot interface if available
        if hasattr(dependency_container, 'bot_interface'):
            bot_interface = dependency_container.bot_interface
        
        # Start the web server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        import logging
        logger = logging.getLogger("homelab.bot")
        logger.error(f"Failed to start web server: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)