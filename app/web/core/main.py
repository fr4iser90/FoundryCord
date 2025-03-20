"""
Main application file for the HomeLab Discord Bot web interface.
"""
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.shared.interface.logging.api import get_bot_logger
from app.web.core.lifecycle_manager import WebLifecycleManager
from app.web.core.workflow_manager import WebWorkflowManager
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.web.core.router_registry import register_routers
from app.web.core.extensions import init_all_extensions
from app.web.core.middleware import setup_middleware

logger = get_bot_logger()

class WebApplication:
    def __init__(self):
        """Initialize the web application."""
        self.service_factory = WebServiceFactory()
        self.lifecycle_manager = WebLifecycleManager()
        self.workflow_manager = WebWorkflowManager()
        self.app = FastAPI(
            title="HomeLab Discord Bot Web Interface",
            description="Web interface for managing HomeLab Discord Bot",
            version="1.0.0"
        )
        
        # 1. ZUERST Templates initialisieren
        self.templates = init_all_extensions(self.app)
        
        # 2. DANN Middleware setup
        setup_middleware(self.app)
        
        # 3. DANN Router registrieren
        register_routers(self.app)
        
        # 4. ZULETZT Manager initialisieren
        self.lifecycle_manager.initialize(self.app, self.service_factory)
        self.workflow_manager.initialize(self.service_factory)
        
        # 5. Base Routes am Ende
        self.setup_base_routes()

    def setup_base_routes(self):
        """Setup basic application routes."""
        @self.app.get("/")
        async def root():
            return {"message": "Welcome to HomeLab Discord Bot"}

        @self.app.get("/api")
        async def api_root():
            return {"message": "HomeLab Discord Bot Web Interface API"}

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}

        @self.app.get("/debug")
        async def debug():
            return {
                "python_path": sys.path,
                "current_directory": os.getcwd(),
                "directory_contents": os.listdir("/app") if os.path.exists("/app") else "Not available"
            }

        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error", "details": str(exc)}
            )

    async def initialize(self):
        """Initialize the web application infrastructure."""
        try:
            # Initialize services
            await self.service_factory.initialize()
            
            # Setup core infrastructure (middleware, routers etc.)
            await self.lifecycle_manager.setup_infrastructure()
            
            # Initialize workflows
            await self.workflow_manager.initialize_workflows()
            
            # Setup lifecycle events
            self.app.on_event("startup")(self.startup_event)
            self.app.on_event("shutdown")(self.shutdown_event)

        except Exception as e:
            logger.error(f"Failed to initialize web application: {e}")
            raise

    async def startup_event(self):
        """Handle application startup."""
        await self.lifecycle_manager.startup()
        await self.workflow_manager.start_workflows()
        await self.workflow_manager.execute_startup_workflow()
        logger.info("Web application started successfully")

    async def shutdown_event(self):
        """Handle application shutdown."""
        await self.workflow_manager.stop_workflows()
        await self.lifecycle_manager.shutdown()

def create_app():
    """Create and configure the application."""
    web_app = WebApplication()
    return web_app.app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)