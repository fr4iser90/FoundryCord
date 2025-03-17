"""Security bootstrapper for generating and managing security keys."""
import os
import base64
from cryptography.fernet import Fernet
import asyncio

from app.shared.interface.logging.api import get_bot_logger

from app.shared.infrastructure.database.repositories.key_repository_impl import KeyRepository
from app.shared.infrastructure.database.core.connection import get_db_connection, ensure_db_initialized

logger = get_bot_logger()

class SecurityBootstrapper:
    """Handles security initialization and key bootstrapping"""
    
    def __init__(self, auto_db_key_management=True):
        self.auto_db_key_management = auto_db_key_management
        self.key_repository = None
        
        # Setup environment variables immediately (sync operation)
        self._ensure_env_keys()
        
    async def initialize(self):
        """Initialize security components"""
        try:
            # First attempt any database operations
            if self.auto_db_key_management:
                await self._initialize_db_keys()
                
            logger.info("Security bootstrapping completed")
            return True
        except Exception as e:
            logger.error(f"Security bootstrapping failed: {e}")
            # Continue without database key storage
            return False
    
    def _ensure_env_keys(self):
        """Ensure all security-related environment variables exist"""
        # Check AES_KEY
        if not os.getenv('AES_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            os.environ['AES_KEY'] = generated_key
            logger.warning(f"Generated missing AES_KEY environment variable: {generated_key[:5]}...")
            
        # Check ENCRYPTION_KEY  
        if not os.getenv('ENCRYPTION_KEY'):
            generated_key = Fernet.generate_key().decode()
            os.environ['ENCRYPTION_KEY'] = generated_key
            logger.warning(f"Generated missing ENCRYPTION_KEY environment variable: {generated_key[:5]}...")
            
        # Check JWT_SECRET_KEY
        if not os.getenv('JWT_SECRET_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
            os.environ['JWT_SECRET_KEY'] = generated_key
            logger.warning(f"Generated missing JWT_SECRET_KEY environment variable: {generated_key[:5]}...")
    
    async def _initialize_db_keys(self):
        """Initialize database key storage"""
        # This is a placeholder - in the real implementation we would:
        # 1. Connect to the database
        # 2. Store the keys in the database
        # For now, we'll just return True to indicate success
        return True
