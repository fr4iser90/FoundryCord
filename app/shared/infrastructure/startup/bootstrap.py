"""Application bootstrap module."""
import asyncio
import logging
from typing import Optional

from app.shared.infrastructure.database.bootstrapper import initialize_database
from app.shared.infrastructure.security.security_bootstrapper import initialize_security
from app.shared.interface.logging.api import get_bot_logger

class ApplicationBootstrap:
    """Class for bootstrapping application components."""
    
    def __init__(self, container_type: str):
        self.container_type = container_type
        self.logger = get_bot_logger()

    async def bootstrap(self) -> bool:
        """
        Bootstrap the complete application with all required services.
        This is the central initialization point for all components.
        
        Returns:
            bool: True if bootstrap was successful, False otherwise
        """
        try:
            # 1. Initialize database first (most critical component)
            self.logger.info("Initializing database...")
            if not await initialize_database():
                self.logger.error("Database initialization failed")
                return False
            
            # 2. Initialize security services
            self.logger.info("Initializing security services...")
            if not await initialize_security():
                self.logger.error("Security initialization failed")
                return False

            self.logger.debug("Application bootstrap completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Application bootstrap failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
