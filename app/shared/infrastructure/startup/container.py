"""Dependency container for application services."""
import logging
from typing import Dict, Any, Type, Optional

logger = logging.getLogger("homelab.bot")

class DependencyContainer:
    """Container for managing application dependencies."""
    
    def __init__(self):
        """Initialize the dependency container."""
        self._services: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}
        
    def register(self, service_type: Type, instance: Any = None, factory: Optional[callable] = None):
        """Register a service with the container.
        
        Args:
            service_type: The type/class of the service
            instance: An optional pre-created instance
            factory: An optional factory function to create instances
        """
        if instance is not None and factory is not None:
            raise ValueError("Cannot register both instance and factory")
            
        self._services[service_type] = {
            'instance': instance,
            'factory': factory
        }
        logger.debug(f"Registered service: {service_type.__name__}")
        
    def resolve(self, service_type: Type) -> Any:
        """Resolve a service from the container.
        
        Args:
            service_type: The type/class of service to resolve
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If the service type is not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service not registered: {service_type.__name__}")
            
        service = self._services[service_type]
        
        # Return existing instance if we have one
        if service['instance'] is not None:
            return service['instance']
            
        # Create new instance if we have a factory
        if service['factory'] is not None:
            instance = service['factory']()
            service['instance'] = instance  # Cache the instance
            return instance
            
        # If no instance or factory, create instance directly
        instance = service_type()
        service['instance'] = instance
        return instance
        
    def clear(self):
        """Clear all registered services."""
        self._services.clear()
        self._instances.clear()