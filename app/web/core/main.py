"""
Main application file for the HomeLab Discord Bot web interface.
"""
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.shared.interfaces.logging.api import get_web_logger
from app.web.core.middleware_registry import register_core_middleware
from app.web.core.extensions import init_extensions
from app.web.core.router_registry import register_routers
from app.web.core.lifecycle_manager import WebLifecycleManager
from app.web.core.workflow_manager import WebWorkflowManager
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from contextlib import asynccontextmanager
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.web.core.exception_handlers import http_exception_handler, generic_exception_handler
# Import the state collector initializer
from app.shared.initializers.state_collectors import register_all_state_collectors

logger = get_web_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Initialize extensions first
    extensions = init_extensions(app)
    app.state.extensions = extensions
    logger.info("Extensions initialized in lifespan context")
    
    # Initialize the application
    try:
        # Setup the application (includes router registration)
        await web_app.setup()
        
        # Initialize workflows
        await web_app.workflow_manager.initialize_workflows()
        
        # Setup lifecycle events
        app.on_event("startup")(web_app.startup_event)
        app.on_event("shutdown")(web_app.shutdown_event)
        
        yield
    finally:
        # Shutdown
        await web_app.shutdown_event()

class WebApplication:
    def __init__(self):
        """Initialize the web application."""
        self.service_factory = WebServiceFactory()
        self.lifecycle_manager = WebLifecycleManager()
        self.workflow_manager = WebWorkflowManager()
        self.app = FastAPI(
            title="HomeLab Discord Bot Web Interface",
            description="Web interface for managing HomeLab Discord Bot",
            version="1.0.0",
            lifespan=lifespan
        )
        # Centralized middleware registration
        register_core_middleware(self.app)
        self._setup_exception_handlers()

    def _setup_exception_handlers(self):
        """Register exception handlers"""
        # Register specific HTTP status code handlers
        for status_code in [400, 401, 403, 404, 500, 503]:
            self.app.add_exception_handler(status_code, http_exception_handler)
        
        # Register catch-all handlers
        self.app.add_exception_handler(HTTPException, http_exception_handler)
        self.app.add_exception_handler(Exception, generic_exception_handler)

    async def setup(self):
        """Setup the web application asynchronously."""
        try:
            # Initialize managers
            self.lifecycle_manager.initialize(self.app, self.service_factory)
            self.workflow_manager.initialize(self.service_factory)
            
            # Register state collectors early in the setup
            register_all_state_collectors()
            
            # Then register routers
            register_routers(self.app)
            
            # Setup base routes
            self.setup_base_routes()
        except Exception as e:
            logger.error(f"Error during application setup: {e}", exc_info=True)
            raise

    def setup_base_routes(self):
        """Setup basic application routes."""
        @self.app.get("/")
        async def root():
            return {"message": "Welcome to HomeLab Discord Bot"}

        @self.app.get("/api")
        async def api_root():
            return {"message": "API root endpoint"}

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

# Create and initialize the application
web_app = WebApplication()
app = web_app.app

async def main():
    """Main entry point for web application"""
    try:
        # Setup is now primarily handled by the lifespan context manager
        # await web_app.setup() # This is called within lifespan now
        
        # Start uvicorn server
        # Pass log_config=None to disable default Uvicorn logging
        config = uvicorn.Config(
            "app.web.core.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True, # Ensure reload is as desired
            log_config=None 
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Error starting web application: {e}", exc_info=True)
        # Consider sys.exit(1) here if startup fails critically
        raise

# Export both app for direct uvicorn and main for entrypoint
__all__ = ['app', 'main']