"""Dependency container for application services."""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("homelab.bot")

class DependencyContainer:
    """Container for application dependencies."""
    
    def __init__(self, config: Dict[str, Any], db_connection, container_type: str):
        """Initialize dependency container."""
        self.config = config
        self.db_connection = db_connection
        self.container_type = container_type
        self.services = {}
        
    def register(self, name: str, service: Any) -> None:
        """Register a service in the container."""
        self.services[name] = service
        logger.debug(f"Registered service: {name}")
        
    def get(self, name: str) -> Optional[Any]:
        """Get a service from the container."""
        return self.services.get(name)
        
    def has(self, name: str) -> bool:
        """Check if a service exists in the container."""
        return name in self.services