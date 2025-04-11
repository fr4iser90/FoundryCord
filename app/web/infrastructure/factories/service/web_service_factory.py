from app.web.infrastructure.factories.base.base_factory import BaseFactory
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.web.application.services.server.server_service import ServerService
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

class WebServiceFactory(BaseFactory):
    _instance = None
    _services = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_services(self):
        """Get or create services"""
        if self._services is None:
            self._services = self.create()
        return self._services
    
    def create(self) -> dict:
        """Create all required web services"""
        services = {}
        try:
            # Use domain services directly
            key_service = KeyManagementService()
            auth_service = AuthenticationService(key_service)  # Domain service
            authz_service = AuthorizationService(auth_service) # Domain service
            server_service = ServerService()
            
            services['key_service'] = key_service
            services['auth_service'] = auth_service
            services['authz_service'] = authz_service
            services['server_service'] = server_service
            
            logger.info("Web services created successfully")
            return services
        except Exception as e:
            logger.error(f"Failed to create web services: {e}")
            raise 