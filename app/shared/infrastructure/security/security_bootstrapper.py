"""Security bootstrapper for generating and managing security keys."""
import logging # Keep standard logging for potential fallback if needed, but prioritize service
import base64
import os
import traceback
from cryptography.fernet import Fernet
from sqlalchemy.exc import SQLAlchemyError
from app.shared.infrastructure.database.session.context import session_context
from app.shared.infrastructure.repositories.auth.key_repository_impl import KeyRepositoryImpl
# Import the shared logger API
from app.shared.interfaces.logging.api import get_shared_logger

# Use the shared logger service instead of standard logging directly
logger = get_shared_logger()

class SecurityBootstrapper:
    """Handles security initialization and key bootstrapping"""
    
    KEY_TYPES = ["AES_KEY", "ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    
    def __init__(self):
        self.key_repository = None
        self.initialized = False
        self.keys = {}
        
    async def initialize(self):
        """Initialize security bootstrapper with database support"""
        if self.initialized:
            logger.debug("Security bootstrapper already initialized")
            return True
            
        try:                    
            # Initialize database repository
            async with session_context() as session:
                self.key_repository = KeyRepositoryImpl(session)
                await self._load_keys_from_database()
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Security bootstrapper initialization failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
    async def _load_keys_from_database(self):
        """Load security keys from database."""
        missing_keys = []
        
        # First check which keys exist in the database
        for key_type in self.KEY_TYPES:
            try:
                # Try to get the key from database
                key_value = await self.key_repository.get_key(key_type)
                
                if key_value:
                    # Key exists in database, use it
                    self.keys[key_type] = key_value
                    logger.debug(f"Loaded {key_type} from database")
                else:
                    # Track missing keys for later generation
                    missing_keys.append(key_type)
                    logger.debug(f"Security key '{key_type}' not found in database")
            except Exception as e:
                logger.error(f"Error checking {key_type}: {str(e)}")
                raise
        
        # Generate only the missing keys, and only once
        if missing_keys:
            self._generate_specific_keys(missing_keys)
            
            # Store all newly generated keys
            for key_type in missing_keys:
                try:
                    await self.key_repository.store_key(key_type, self.keys[key_type])
                    logger.debug(f"Stored {key_type} in database")
                except Exception as e:
                    logger.error(f"Error storing {key_type}: {str(e)}")
                    raise
    
    def _generate_specific_keys(self, key_types):
        """Generate specific security keys in memory."""
        for key_type in key_types:
            # Generate a new key
            if key_type in ["AES_KEY", "ENCRYPTION_KEY"]:
                new_key = Fernet.generate_key().decode('utf-8')
            else:  # JWT_SECRET_KEY
                new_key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
            
            # Store the key in memory
            self.keys[key_type] = new_key
            
            # Log the generation (hide part of the key)
            visible_part = new_key[:5] + "..." if len(new_key) > 5 else new_key
            logger.debug(f"Generated {key_type} in memory: {visible_part}")
    
    def get_key(self, key_type):
        """Get a security key by type."""
        # --- DEBUG LOGGING --- 
        logger.debug(f"[SecurityBootstrapper] Attempting to get key: {key_type}")
        logger.debug(f"[SecurityBootstrapper] Current keys in memory: {list(self.keys.keys())}") # Log only keys for brevity
        logger.debug(f"[SecurityBootstrapper] Is initialized: {self.initialized}")
        # --- END DEBUG LOGGING ---
        
        if key_type not in self.KEY_TYPES:
            logger.error(f"[SecurityBootstrapper] Unknown key type requested: {key_type}")
            raise ValueError(f"Unknown key type: {key_type}")
        
        key_value = self.keys.get(key_type)
        if not key_value:
             logger.warning(f"[SecurityBootstrapper] Key '{key_type}' not found in memory cache (self.keys).")
        
        return key_value

# Global instance
_security_bootstrapper = SecurityBootstrapper()

async def initialize_security() -> bool:
    """Initialize the security system."""
    return await _security_bootstrapper.initialize()

def get_security_bootstrapper() -> SecurityBootstrapper:
    """Get the global security bootstrapper instance."""
    return _security_bootstrapper
