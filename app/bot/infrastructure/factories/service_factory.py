"""Service factory for creating and managing services."""
from typing import Dict, Any, Optional, Callable
import importlib
import inspect
import asyncio
import os
import logging

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceFactory:
    """Factory for creating and managing services."""
    
    def __init__(self, bot):
        """Initialize the ServiceFactory."""
        # --- ADD DEBUG LOG ---
        bot_id = getattr(bot.user, 'id', 'N/A') if bot and hasattr(bot, 'user') else 'Bot Invalid'
        logger.info(f"[DEBUG ServiceFactory.__init__] Initializing with bot ID: {bot_id}")
        # --- END DEBUG LOG ---
        self.bot = bot
        self._services: Dict[str, Any] = {} # Cache for created services
        self._creators: Dict[str, Callable] = {} # For lazy loading/creation functions

        # --- ADD DEBUG LOG AT END ---
        try:
            num_services = len(self._services)
            logger.info(f"[DEBUG ServiceFactory.__init__] Initialization complete. Bot ID: {bot_id}. Initial services registered: {num_services}")
        except Exception as e:
             logger.error(f"[DEBUG ServiceFactory.__init__] Error during final log: {e}")
        # --- END DEBUG LOG ---

    def register_service_creator(self, name: str, creator: Callable, overwrite: bool = False):
        """Registers a function that creates a service instance (lazy loading)."""
        if name in self._creators and not overwrite:
            logger.warning(f"Service creator '{name}' already registered. Set overwrite=True to replace.")
            return
        self._creators[name] = creator
        logger.debug(f"Registered service creator for '{name}'.")

    def register_service(self, name: str, instance: Any, overwrite: bool = False):
        """Registers an already created service instance."""
        if name in self._services and not overwrite:
             logger.warning(f"Service instance '{name}' already registered. Set overwrite=True to replace.")
             return
        self._services[name] = instance
        logger.info(f"Registered service instance '{name}' of type {type(instance).__name__}.")

    def get_service(self, name: str) -> Optional[Any]:
        """Gets a service instance, creating it if necessary using a registered creator."""
        if name in self._services:
            return self._services[name]

        if name in self._creators:
            logger.debug(f"Service '{name}' not found in cache, attempting creation via registered creator.")
            try:
                creator_func = self._creators[name]
                # Assume creator function takes the bot instance if needed
                # You might need a more sophisticated way to pass arguments if creators vary
                instance = creator_func(self.bot)
                if instance:
                    logger.info(f"Successfully created service '{name}' via creator. Type: {type(instance).__name__}")
                    self._services[name] = instance # Cache the created instance
                    return instance
                else:
                    logger.error(f"Service creator for '{name}' returned None.")
                    return None
            except Exception as e:
                logger.error(f"Error creating service '{name}' via creator: {e}", exc_info=True)
                return None
        else:
            logger.error(f"Service '{name}' not found. No instance registered and no creator available.")
            return None

    def has_service(self, name: str) -> bool:
        """Checks if a service instance or creator is registered."""
        return name in self._services or name in self._creators

    async def initialize_services(self):
        """Initialize registered services that have initialize method."""
        for name, service in self._services.items():
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
        return self._services.copy() 