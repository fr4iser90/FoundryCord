from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class WebCompositeFactory:
    def __init__(self):
        self.service_factory = WebServiceFactory()

    def create_all(self) -> dict:
        """Create all web components"""
        try:
            services = self.service_factory.create()
            logger.info("All web components created successfully")
            return services
        except Exception as e:
            logger.error(f"Failed to create web components: {e}")
            raise 