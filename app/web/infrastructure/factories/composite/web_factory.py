from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

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