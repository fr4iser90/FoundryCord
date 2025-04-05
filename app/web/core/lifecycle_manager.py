from typing import Dict, List, Any, Optional, Callable
import asyncio
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.interface.logging.api import get_web_logger
from fastapi import FastAPI
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory

logger = get_web_logger()

class WebLifecycleManager:
    """Manages the lifecycle of the web application."""
    
    def __init__(self):
        """Initialize the lifecycle manager."""
        self.app = None
        self.service_factory = None
        self.state = "initializing"
        self.shutdown_hooks = []
        self.startup_hooks = []
        self.components = {}
        self.services_initialized = False

        # Register core services
        self._register_core_services()

    def _register_core_services(self):
        """Register core services that should be available"""
        try:
            # Create and register key service
            key_service = KeyManagementService()
            self.register_component('key_service', key_service)

            # Create and register auth service
            auth_service = WebAuthenticationService(key_service)
            self.register_component('auth_service', auth_service)

            logger.info("Core services registered successfully")
        except Exception as e:
            logger.error(f"Failed to register core services: {e}")
            raise

    def register_shutdown_hook(self, hook: Callable):
        """Register a function to be called during shutdown"""
        self.shutdown_hooks.append(hook)
        logger.debug(f"Registered shutdown hook: {hook.__name__}")
    
    def register_startup_hook(self, hook: Callable):
        """Register a function to be called during startup"""
        self.startup_hooks.append(hook)
        logger.debug(f"Registered startup hook: {hook.__name__}")
    
    async def on_startup(self):
        """Execute all registered startup hooks and initialize services"""
        logger.info("Executing startup hooks")
        self.state = "starting"
        
        # Initialize registered services
        for name, service in self.components.items():
            if hasattr(service, 'initialize'):
                try:
                    await service.initialize()
                    logger.info(f"Initialized service: {name}")
                except Exception as e:
                    logger.error(f"Failed to initialize service {name}: {e}")
                    raise
        
        # Execute startup hooks
        for hook in self.startup_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                logger.error(f"Error in startup hook {hook.__name__}: {e}")
                raise
        
        self.state = "running"
        self.services_initialized = True
        logger.info("Startup complete")
    
    async def on_shutdown(self):
        """Execute all registered shutdown hooks"""
        logger.info("Executing shutdown hooks")
        self.state = "shutting_down"
        
        for hook in self.shutdown_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                logger.error(f"Error in shutdown hook {hook.__name__}: {e}")
        
        self.state = "shutdown"
        logger.info("Shutdown complete")
    
    def register_component(self, name: str, component: Any):
        """Register a component with the lifecycle manager"""
        self.components[name] = component
        logger.debug(f"Registered component: {name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component by name"""
        return self.components.get(name)
    
    def get_state(self) -> str:
        """Get the current lifecycle state"""
        return self.state

    def initialize(self, app: FastAPI, service_factory: WebServiceFactory):
        """Initialize with app and service factory."""
        self.app = app
        self.service_factory = service_factory
        
    async def setup_infrastructure(self):
        """Setup core infrastructure components."""
        try:
            # Setup CORS
            from fastapi.middleware.cors import CORSMiddleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Setup session middleware
            from app.web.core.middleware import setup_session_middleware
            await setup_session_middleware(self.app)
            
            # Register routers
            from app.web.core.router_registry import register_routers
            register_routers(self.app)
            
            logger.info("Web infrastructure setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup web infrastructure: {e}")
            raise
            
    async def startup(self):
        """Handle application startup tasks."""
        try:
            # Initialize services
            await self.service_factory.initialize_services()
            logger.info("Web application startup completed")
            
        except Exception as e:
            logger.error(f"Failed during web application startup: {e}")
            raise
            
    async def shutdown(self):
        """Handle application shutdown tasks."""
        try:
            # Cleanup services
            await self.service_factory.cleanup_services()
            logger.info("Web application shutdown completed")
            
        except Exception as e:
            logger.error(f"Failed during web application shutdown: {e}")
            raise