"""Service factory for creating and managing services."""
from typing import Dict, Any, Optional, Callable
import importlib
import inspect
import asyncio
import os
import logging

from app.bot.application.interfaces.service_factory import ServiceFactory as ServiceFactoryInterface
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceFactory(ServiceFactoryInterface):
    """Factory for creating and managing services."""
    
    def __init__(self, bot):
        """Initialize the ServiceFactory."""
        # --- ADD DEBUG LOG ---
        bot_id = getattr(bot.user, 'id', 'N/A') if bot and hasattr(bot, 'user') else 'Bot Invalid'
        logger.debug(f"[DEBUG ServiceFactory.__init__ SIMPLIFIED] Initializing with bot ID: {bot_id}")
        # --- END DEBUG LOG ---
        self.bot = bot
        # --- Use simple dictionary for storage ---
        self._services: Dict[str, Any] = {} 
        self._creators: Dict[str, Callable] = {} 
        logger.debug(f"[DEBUG ServiceFactory.__init__ SIMPLIFIED] Initialization complete. Bot ID: {bot_id}")

    def register_service_creator(self, name, creator, overwrite = False):
        """Registers a function that creates a service instance (lazy loading)."""
        if name in self._creators and not overwrite:
            logger.warning(f"Service creator '{name}' already registered. Set overwrite=True to replace.")
            return
        self._creators[name] = creator
        logger.debug(f"Registered service creator for '{name}'.")

    def register_service(self, name, instance, overwrite = False):
        """Registers an already created service instance."""
        if name in self._services and not overwrite:
             logger.warning(f"Service instance '{name}' already registered. Set overwrite=True to replace.")
             return
        self._services[name] = instance
        logger.debug(f"Registered service instance '{name}' of type {type(instance).__name__}.")

    def get_service(self, name):
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
                    logger.debug(f"Successfully created service '{name}' via creator. Type: {type(instance).__name__}")
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

    def has_service(self, name):
        """Checks if a service instance or creator is registered."""
        return name in self._services or name in self._creators

    async def initialize_services(self):
        """Initialize registered services that have an initialize method."""
        logger.debug("Initializing registered services...")
        overall_success = True

        # --- Ensure ComponentRegistry is initialized first ---
        try:
            # Use get_service which handles creation/retrieval
            component_registry = self.get_service('component_registry')
            if component_registry and hasattr(component_registry, 'initialize') and callable(component_registry.initialize):
                 logger.debug("Attempting to initialize ComponentRegistry (load DB definitions)...")
                 # Ensure bot instance is available
                 if not self.bot:
                     logger.error("Cannot initialize ComponentRegistry: Bot instance not available in ServiceFactory.")
                     overall_success = False
                 else:
                    # Call initialize on the retrieved/created component_registry instance
                    init_success = await component_registry.initialize(self.bot)
                    if not init_success:
                         logger.error("ComponentRegistry initialization failed.")
                         overall_success = False # Mark as failed if registry init fails
                    else:
                         logger.debug("ComponentRegistry initialized successfully.")
            elif component_registry:
                 logger.debug("ComponentRegistry found but has no initialize method.")
            else:
                 # This case might indicate an issue if component_registry should always be registered
                 logger.warning("ComponentRegistry service not found via get_service. Skipping its initialization.")
                 # Depending on requirements, maybe overall_success = False here?
        except Exception as reg_init_err:
            logger.error(f"Error during specific initialization of ComponentRegistry: {reg_init_err}", exc_info=True)
            overall_success = False
        # --- End ComponentRegistry Initialization ---

        # --- Initialize other services ---
        logger.debug("Initializing other registered services...")
        services_to_init = list(self._services.items())
        for name, service in services_to_init:
            # Skip ComponentRegistry as we explicitly initialized it above
            if name == 'component_registry':
                continue

            if hasattr(service, 'initialize') and callable(service.initialize):
                try:
                    logger.debug(f"Initializing service: {name}...")
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                    logger.debug(f"Successfully initialized service: {name}")
                except Exception as e:
                    logger.error(f"Error initializing service {name}: {e}", exc_info=True)
                    overall_success = False

        logger.debug(f"Service initialization process completed. Overall success: {overall_success}")
        return overall_success
    
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