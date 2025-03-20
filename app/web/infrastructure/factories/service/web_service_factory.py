from app.web.infrastructure.factories.base.base_factory import BaseFactory
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class WebServiceFactory(BaseFactory):
    def create(self) -> dict:
        """Create all required web services"""
        services = {}
        try:
            services['key_service'] = KeyManagementService()
            services['auth_service'] = WebAuthenticationService(services['key_service'])
            logger.info("Web services created successfully")
            return services
        except Exception as e:
            logger.error(f"Failed to create web services: {e}")
            raise 