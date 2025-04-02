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
from app.shared.interface.logging.api import get_web_logger
from app.web.core.middleware import setup_middleware
from app.web.core.extensions import init_all_extensions
from app.web.core.router_registry import register_routers
from app.web.core.lifecycle_manager import WebLifecycleManager
from app.web.core.workflow_manager import WebWorkflowManager
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from contextlib import asynccontextmanager
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.web.core.exception_handlers import http_exception_handler, generic_exception_handler

logger = get_web_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup
    await web_app.initialize()
    yield
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
        self._setup_middleware()
        self._setup_exception_handlers()

    def _setup_middleware(self):
        """Setup middleware during initialization"""
        # Setup Session FIRST
        session_secret = os.environ.get("JWT_SECRET_KEY", os.urandom(32).hex())

        from app.web.core.middleware import auth_middleware
        self.app.middleware("http")(auth_middleware)
        logger.info("Auth middleware registered successfully")        
        
        from starlette.middleware.sessions import SessionMiddleware
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=session_secret,
            session_cookie="homelab_session",
            max_age=7 * 24 * 60 * 60,  # 1 week
            same_site="lax",
            https_only=True
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        

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
            # Initialize templates
            self.templates = init_all_extensions(self.app)
            

            
            # Then register routers
            register_routers(self.app)
            
            # Initialize managers
            self.lifecycle_manager.initialize(self.app, self.service_factory)
            self.workflow_manager.initialize(self.service_factory)
            
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


    async def initialize(self):
        """Initialize the web application."""
        try:
            # Setup the application
            await self.setup()
            
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

# Create and initialize the application
web_app = WebApplication()
app = web_app.app

# This is the entry point for Uvicorn
if __name__ == "__main__":
    uvicorn.run("app.web.core.main:app", host="0.0.0.0", port=8000)