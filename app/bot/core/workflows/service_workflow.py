from .base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceWorkflow(BaseWorkflow):
    async def initialize(self):
        try:
            logger.debug("Starting service workflow initialization")
            
            # Use existing factory pattern for services
            for service_config in self.bot.critical_services:
                service = self.bot.factory.create_service(
                    service_config['name'],
                    service_config['setup']
                )
                await self.bot.lifecycle._initialize_service(service)
                
            for service_config in self.bot.module_services:
                service = self.bot.factory.create_service(
                    service_config['name'],
                    service_config['setup']
                )
                await self.bot.lifecycle._initialize_service(service)
                
            return True
            
        except Exception as e:
            logger.error(f"Service workflow initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup service resources"""
        try:
            for service in reversed(self.bot.lifecycle.services):
                await service.cleanup()
        except Exception as e:
            logger.error(f"Service cleanup failed: {e}")
