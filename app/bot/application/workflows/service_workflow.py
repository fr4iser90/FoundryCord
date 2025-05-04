"""Service workflow for managing service operations."""
from typing import Dict, Any, List, Optional
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_workflow import BaseWorkflow

class ServiceWorkflow(BaseWorkflow):
    """Workflow for managing services."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.services = {}
        
    async def initialize(self):
        """Initialize the service workflow."""
        try:
            service_types = [
                'wireguard',
                'monitoring',
                'backups',
                'system_metrics'
            ]
            
            for service_type in service_types:
                service_config = {
                    'name': service_type,
                    'type': service_type
                }
                
                try:
                    # Try to initialize the service
                    service = await self.bot.lifecycle._initialize_service(service_config)
                    if service:
                        self.services[service_type] = service
                        logger.info(f"Service {service_type} initialized")
                    else:
                        logger.warning(f"Service {service_type} not available")
                except Exception as e:
                    logger.error(f"Error initializing service {service_type}: {e}")
                    # Continue with other services
            
            logger.info(f"Service workflow initialized with {len(self.services)} services")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing service workflow: {e}")
            return False
    
    async def get_service(self, service_type: str):
        """Get a service by type."""
        return self.services.get(service_type)
    
    async def execute_service_command(self, service_type: str, command: str, *args, **kwargs):
        """Execute a command on a service."""
        service = await self.get_service(service_type)
        
        if not service:
            logger.error(f"Service {service_type} not available")
            return None
            
        if not hasattr(service, command) or not callable(getattr(service, command)):
            logger.error(f"Command {command} not supported by service {service_type}")
            return None
            
        try:
            # Execute the command
            command_func = getattr(service, command)
            if asyncio.iscoroutinefunction(command_func):
                return await command_func(*args, **kwargs)
            else:
                return command_func(*args, **kwargs)
                
        except Exception as e:
            logger.error(f"Error executing command {command} on service {service_type}: {e}")
            return None
    
    async def cleanup(self):
        """Clean up service workflow resources."""
        for service_type, service in self.services.items():
            if hasattr(service, 'cleanup') and callable(service.cleanup):
                try:
                    # Cleanup service
                    if asyncio.iscoroutinefunction(service.cleanup):
                        await service.cleanup()
                    else:
                        service.cleanup()
                        
                    logger.debug(f"Cleaned up service: {service_type}")
                except Exception as e:
                    logger.error(f"Error cleaning up service {service_type}: {e}")
                    
        logger.info("Service workflow cleaned up")
        return True
