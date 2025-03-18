"""Security bootstrapper for generating and managing security keys."""
import os
import base64
import logging
import traceback
from cryptography.fernet import Fernet
import asyncio

from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.repositories.key_repository_impl import KeyRepository
from app.shared.infrastructure.database.core.connection import get_db_connection, ensure_db_initialized
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.database.core.init import create_tables
from app.shared.infrastructure.database.models.base import initialize_engine
from app.shared.infrastructure.database.api import get_session

logger = logging.getLogger("homelab.bot")

class SecurityBootstrapper:
    """Handles security initialization and key bootstrapping"""
    
    KEY_TYPES = ["AES_KEY", "ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    
    def __init__(self, auto_db_key_management=True):
        self.auto_db_key_management = auto_db_key_management
        self.key_repository = None
        
        # We'll defer key setup to the async initialize method
        # This allows proper database interaction
    
    async def initialize(self):
        """Initialize security bootstrapper with database support"""
        try:
            # Ensure environment variables are set
            self._ensure_env_keys()
            
            if self.auto_db_key_management:
                # Try to load keys from database
                try:
                    await self._load_keys_from_database()
                    logger.info("Security keys loaded from database successfully")
                except Exception as e:
                    logger.error(f"Failed to load keys from database: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Continue with environment variables as fallback
                    logger.warning("Using environment variables as fallback for security keys")
            
            return True
        except Exception as e:
            logger.error(f"Security bootstrapper initialization failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _ensure_env_keys(self):
        """Ensure all required security keys exist as environment variables."""
        for key_type in self.KEY_TYPES:
            if not os.environ.get(key_type):
                # Generate a new key
                if key_type == "AES_KEY" or key_type == "ENCRYPTION_KEY":
                    new_key = Fernet.generate_key().decode('utf-8')
                else:  # JWT_SECRET_KEY
                    new_key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
                
                # Set the environment variable
                os.environ[key_type] = new_key
                
                # Log the generation (hide part of the key)
                visible_part = new_key[:5] + "..." if len(new_key) > 5 else new_key
                logger.warning(f"Generated missing {key_type} environment variable: {visible_part} (NOT PERSISTED)")
    
    async def _load_keys_from_database(self):
        """Load security keys from database."""
        # Initialize key repository with a proper session
        session = await get_session()
        self.key_repository = KeyRepository(session)
        
        # Load each key from database
        for key_type in self.KEY_TYPES:
            try:
                # Try to get the key from database
                key_value = await self.key_repository.get_key(key_type)
                
                if key_value:
                    # Key exists in database, use it
                    os.environ[key_type] = key_value
                    logger.info(f"Loaded {key_type} from database")
                else:
                    # Key doesn't exist in database, store the current one
                    current_key = os.environ.get(key_type)
                    if current_key:
                        # Store the current key in database
                        await self.key_repository.store_key(key_type, current_key)
                        logger.info(f"Stored {key_type} in database")
            except Exception as e:
                logger.error(f"Error loading/storing {key_type}: {str(e)}")
                # Continue with next key
