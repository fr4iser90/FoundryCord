"""Database credential management module."""
import os
import logging
import asyncio
from typing import Dict, Any, Optional

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Controls whether credentials are automatically managed
AUTO_DB_CREDENTIAL_MANAGEMENT = True

class DatabaseCredentialManager:
    """Manages database credentials and connection settings with secure storage."""
    
    def __init__(self, environment_variables: bool = True):
        """Initialize the credential manager.
        
        Args:
            environment_variables: Whether to get credentials from environment variables
        """
        self.environment_variables = environment_variables
        self._credentials = None
        self._initialized = False
        self._repository = None  # Will be initialized async
    
    async def initialize(self):
        """Async initialization with database repository setup."""
        if not self._initialized:
            try:
                # Import here to avoid circular imports
                from app.shared.domain.repositories.auth.key_repository import KeyRepository
                from app.shared.infrastructure.database.session.factory import get_session
                
                # Initialize repository for credential storage
                session = await get_session()
                self._repository = KeyRepository(session)
                
                # Load/initialize credentials
                await self._initialize_credentials()
                
                self._initialized = True
                return True
            except Exception as e:
                logger.error(f"Failed to initialize database credential manager: {e}")
                return False
        return True
    
    async def _initialize_credentials(self):
        """Initialize credentials, potentially generating if needed."""
        # For the initial setup, we must use environment variables
        env_creds = self._get_env_credentials()
        
        # Store the initial credentials if AUTO_DB_CREDENTIAL_MANAGEMENT is enabled
        if AUTO_DB_CREDENTIAL_MANAGEMENT and self._repository:
            # Check if credentials are already stored
            db_creds = await self._repository.get_db_credentials()
            if not db_creds:
                # Store initial credentials from environment
                await self._repository.store_db_credentials(env_creds)
                logger.info("Initial database credentials stored in secure storage")
        
        # Set credentials for use
        self._credentials = env_creds
    
    def get_credentials(self) -> Dict[str, Any]:
        """Get database credentials from appropriate source.
        
        Returns:
            Dict with database connection credentials
        """
        if self._credentials:
            return self._credentials
            
        # Read credentials from environment variables
        if self.environment_variables:
            return self._get_env_credentials()
        
        # Fallback to secure storage (in production implement)
        return self._get_secure_credentials()
    
    async def get_async_credentials(self) -> Dict[str, Any]:
        """Get credentials with async repository support.
        
        Returns:
            Dict with database connection credentials
        """
        # If already loaded, return them
        if self._credentials:
            return self._credentials
            
        # If AUTO_DB_CREDENTIAL_MANAGEMENT is enabled and repository is available
        if AUTO_DB_CREDENTIAL_MANAGEMENT and self._repository:
            # Try to get credentials from database
            db_creds = await self._repository.get_db_credentials()
            if db_creds:
                self._credentials = db_creds
                return db_creds
        
        # Fallback to environment variables
        return self._get_env_credentials()
    
    def _get_env_credentials(self) -> Dict[str, Any]:
        """Get credentials from environment variables.
        
        Returns:
            Dict with database connection credentials
        """
        # Required environment variables
        required_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'APP_DB_USER', 'APP_DB_PASSWORD', 'POSTGRES_DB']
        
        # Check if all required variables are present
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            logger.error(f"Missing required database environment variables: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required environment variables for database connection")
            
        # Secure use of environment variables without fallbacks
        creds = {
            'host': os.environ['POSTGRES_HOST'],
            'port': int(os.environ['POSTGRES_PORT']),
            'user': os.environ['APP_DB_USER'],
            'password': os.environ['APP_DB_PASSWORD'],
            'database': os.environ['POSTGRES_DB']
        }
        
        self._credentials = creds
        return creds
    
    def _get_secure_credentials(self) -> Dict[str, Any]:
        """Get credentials from secure storage (implementation needed).
        
        Returns:
            Dict with database connection credentials
        """
        # In production: Implement with secure storage (Vault, KMS, etc.)
        raise NotImplementedError("Secure credential storage not implemented")
