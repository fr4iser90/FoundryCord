"""Service configuration using factory pattern."""
from typing import List, Dict, Any
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceConfig:
    @staticmethod
    def register_critical_services(bot) -> List[Dict[str, Any]]:
        """Use factory pattern to create critical services"""
        logger.info("Creating critical services using factory pattern")
        
        # Use the service factory instead of hardcoded config
        service_factory = bot.component_factory.create_service_factory()
        services = []
        
        # Register critical services using the factory
        logger.info(f"Registered {len(services)} critical services using factory pattern")
        return services
    
    @staticmethod
    def register_module_services(bot) -> List[Dict[str, Any]]:
        """Use factory pattern to create module services"""
        logger.info("Creating module services using factory pattern")
        
        # Use the factory pattern for all module services
        service_factory = bot.component_factory.create_service_factory()
        workflow_factory = bot.component_factory.create_workflow_factory()
        
        # Create services list
        services = []
        
        # No more direct reference to DashboardConfig
        # Dashboard functionality is now handled through the workflow factory
        
        logger.info(f"Registered {len(services)} module services using factory pattern")
        return services