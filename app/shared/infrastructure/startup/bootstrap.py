"""Application bootstrap process."""
import asyncio
import logging
import traceback
from typing import Optional, Dict, Any

from app.shared.infrastructure.config.env_manager import EnvManager
from app.shared.infrastructure.database.core.connection import get_db_connection
from app.shared.infrastructure.database.core.init import wait_for_database
from app.shared.infrastructure.security.security_bootstrapper import SecurityBootstrapper
from app.shared.infrastructure.startup.container import DependencyContainer
from app.shared.infrastructure.startup.sequence import StartupSequence

logger = logging.getLogger("homelab.bot")

class ApplicationBootstrap:
    """Handles application bootstrap process."""
    
    def __init__(self, container_type: str):
        """Initialize bootstrap with container type."""
        self.container_type = container_type
        self.env_manager = EnvManager()
        self.config = None
        self.dependency_container = None
        self.startup_sequence = None
    
    async def initialize(self) -> bool:
        """Initialize the application."""
        try:
            logger.info(f"===== Homelab Discord Bot {self.container_type.capitalize()} Initialization =====")
            logger.info(f"Running in {self.container_type.upper()} container mode")
            
            # Load environment configuration
            self.config = self.env_manager.configure()
            
            # Initialize security for environment variables
            security = SecurityBootstrapper(auto_db_key_management=False)
            security._ensure_env_keys()
            
            # Wait for database with retry logic
            if not await self._wait_for_database():
                return False
                
            # Initialize database connection
            logger.info("Initializing database connection")
            db_conn = await get_db_connection()
            logger.info("Database connection initialized successfully")
            
            # Initialize security with database support
            try:
                logger.info("Initializing security key storage...")
                security = SecurityBootstrapper(auto_db_key_management=True)
                await security.initialize()
            except Exception as e:
                logger.error(f"Security bootstrapping failed: {str(e)}")
                # Continue with environment variables
            
            # Create dependency container
            self.dependency_container = DependencyContainer(
                config=self.config,
                db_connection=db_conn,
                container_type=self.container_type
            )
            
            # Create and run startup sequence
            self.startup_sequence = StartupSequence(self.dependency_container)
            if self.container_type == "bot":
                await self.startup_sequence.run_bot_sequence()
            elif self.container_type == "web":
                await self.startup_sequence.run_web_sequence()
            
            logger.info(f"{self.container_type.capitalize()} initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"{self.container_type.capitalize()} initialization failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    async def _wait_for_database(self) -> bool:
        """Wait for database with retry logic."""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Database readiness check (attempt {attempt}/{max_retries})...")
            if await wait_for_database():
                logger.info(f"Database is ready for {self.container_type} initialization")
                return True
                
            if attempt < max_retries:
                logger.info(f"Waiting {retry_delay}s before retrying...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        logger.error("Database not available after maximum retries")
        return False