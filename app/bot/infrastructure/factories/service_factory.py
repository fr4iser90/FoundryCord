"""Service factory for creating and managing services."""
from typing import Dict, Any, Optional
import importlib
import inspect
import asyncio
import os

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceFactory:
    """Factory for creating and managing services."""
    
    def __init__(self, bot):
        self.bot = bot
        self.services = {}
        self.initialized = False
    
    def register_service(self, service_name: str, service_instance):
        """Register a service instance."""
        self.services[service_name] = service_instance
        logger.debug(f"Registered service: {service_name}")
        
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service by name."""
        return self.services.get(service_name)
    
    async def initialize_services(self):
        """Initialize registered services that have initialize method."""
        for name, service in self.services.items():
            if hasattr(service, 'initialize') and callable(service.initialize):
                try:
                    # Check if initialize is a coroutine function
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                    logger.debug(f"Initialized service: {name}")
                except Exception as e:
                    logger.error(f"Error initializing service {name}: {e}")
        
        self.initialized = True
        return True
    
    def create(self, service_type: str, *args, **kwargs) -> Optional[Any]:
        """Create a service instance."""
        try:
            # Try to determine the module path based on service name
            # Fix the capitalization - convert service_type to proper module path format
            module_name = service_type.replace(' ', '_').lower()
            
            # First try the standard location
            module_paths = [
                f"app.bot.application.services.{module_name}.{module_name}_service",
                f"app.bot.application.services.{module_name}",
                f"app.shared.application.services.{module_name}.{module_name}_service",
                f"app.shared.application.services.{module_name}"
            ]
            
            # Determine class name - CamelCase with "Service" suffix
            class_name = "".join(word.capitalize() for word in service_type.replace(' ', '_').split('_')) + "Service"
            
            # Try each module path
            service_class = None
            for module_path in module_paths:
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, class_name):
                        service_class = getattr(module, class_name)
                        break
                except ImportError:
                    continue
                
            if not service_class:
                logger.error(f"Service class not found for type: {service_type} (tried {class_name})")
                return None
            
            # Create service instance
            service = service_class(self.bot, *args, **kwargs)
            
            # Register the service
            safe_name = service_type.replace(' ', '_').lower()
            self.register_service(safe_name, service)
            
            return service
            
        except Exception as e:
            logger.error(f"Error creating service {service_type}: {e}")
            return None
            
    def create_or_get(self, service_type: str, *args, **kwargs) -> Optional[Any]:
        """Get an existing service or create a new one."""
        safe_name = service_type.replace(' ', '_').lower()
        existing = self.get_service(safe_name)
        if existing:
            return existing
            
        return self.create(service_type, *args, **kwargs)
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all registered services."""
        return self.services.copy() 