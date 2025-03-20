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
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import secrets

# Import app components
from app.web.infrastructure.security.auth import get_current_user
from app.web.core.middleware import role_check_middleware
from app.web.core.router_registry import register_routers
from app.web.core.workflows.service_workflow import WebServiceWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.web.core.lifecycle_manager import WebLifecycleManager
from app.web.core.workflow_manager import WebWorkflowManager

logger = get_bot_logger()

class HomelabWebApp:
    def __init__(self):
        # FastAPI app
        self.app = FastAPI(title="HomeLab Discord Bot Web Interface")
        
        # Initialize managers FIRST
        self.lifecycle = WebLifecycleManager()
        self.workflow_manager = WebWorkflowManager()
        
        # Setup session middleware SECOND
        secret_key = secrets.token_urlsafe(32)
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=secret_key,
            session_cookie="homelab_session",
            max_age=86400  # 24 hours
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add custom role middleware
        self.app.middleware("http")(role_check_middleware)
        
        # Register startup/shutdown events
        self.app.add_event_handler("startup", self.startup_event)
        self.app.add_event_handler("shutdown", self.shutdown_event)
        
        # Register routers (this will also mount static files)
        register_routers(self.app)

    async def startup_event(self):
        """Initialize on startup"""
        try:
            # Initialize lifecycle and workflow managers
            await self.lifecycle.on_startup()
            await self.workflow_manager.initialize_all()
            
            logger.info("Web application started successfully")
        except Exception as e:
            logger.error(f"Failed to start web application: {e}")
            raise

    async def shutdown_event(self):
        """Cleanup on shutdown"""
        try:
            await self.lifecycle.on_shutdown()
            logger.info("Web application shutdown successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create single application instance
app = HomelabWebApp()
# Export FastAPI instance for ASGI servers
fastapi_app = app.app

# API root endpoint
@fastapi_app.get("/api")
async def api_root():
    return {
        "message": "HomeLab Discord Bot Web Interface API",
        "bot_interface_available": bot_interface is not None
    }

# Health check endpoint
@fastapi_app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot_interface": "available" if bot_interface is not None else "unavailable"
    }

# Debug endpoint to show Python path and available modules
@fastapi_app.get("/debug")
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
@fastapi_app.exception_handler(Exception)
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
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
    except Exception as e:
        import logging
        logger = logging.getLogger("homelab.bot")
        logger.error(f"Failed to start web server: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)