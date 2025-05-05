"""Application bootstrap module."""
import asyncio
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.security import initialize_security, get_security_bootstrapper
from app.shared.infrastructure.database.migrations.migration_service import MigrationService

class ApplicationBootstrap:
    """Class for bootstrapping application components."""
    
    def __init__(self, container_type: str):
        self.container_type = container_type
        self.logger = get_db_logger()
        self.db_service = DatabaseService()
        self.security_bootstrapper = None

    async def initialize_database(self) -> bool:
        """Initialize database and run migrations."""
        try:
            # 1. Initialize database service
            if not await self.db_service.initialize():
                self.logger.error("Failed to initialize database service")
                return False

            # 2. Run migrations
            migration_service = MigrationService()
            if not await migration_service.check_migrations():
                self.logger.error("Database migrations failed")
                return False

            self.logger.debug("Database initialization completed")
            return True
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False

    async def initialize_security_components(self) -> bool:
        """Initialize security components."""
        try:
            # Initialize security bootstrapper
            if not await initialize_security():
                self.logger.error("Failed to initialize security")
                return False
                
            # Get security bootstrapper instance
            self.security_bootstrapper = get_security_bootstrapper()
            if not self.security_bootstrapper:
                self.logger.error("Failed to get security bootstrapper")
                return False
                
            self.logger.debug("Security components initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Security initialization failed: {e}")
            return False

    async def bootstrap(self) -> bool:
        """
        Bootstrap the complete application with all required services.
        This is the central initialization point for all components.
        
        Returns:
            bool: True if bootstrap was successful, False otherwise
        """
        try:
            # 1. Initialize database and run migrations
            if not await self.initialize_database():
                self.logger.error("Database initialization failed")
                return False

            # 2. Initialize security components
            if not await self.initialize_security_components():
                self.logger.error("Security initialization failed")
                return False

            self.logger.debug("Application bootstrap completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Application bootstrap failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
