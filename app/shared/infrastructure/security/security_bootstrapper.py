"""Security bootstrapper for generating and managing security keys."""
import os
import base64
from cryptography.fernet import Fernet
import asyncio

from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.repositories.key_repository_impl import KeyRepository
from app.shared.infrastructure.database.core.connection import get_db_connection, ensure_db_initialized
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.database.core.init import create_tables
from app.shared.infrastructure.database.models.base import initialize_engine

logger = get_bot_logger()

class SecurityBootstrapper:
    """Handles security initialization and key bootstrapping"""
    
    KEY_TYPES = ["AES_KEY", "ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    
    def __init__(self, auto_db_key_management=True):
        self.auto_db_key_management = auto_db_key_management
        self.key_repository = None
        
        # We'll defer key setup to the async initialize method
        # This allows proper database interaction
    
    async def initialize(self):
        """Initialize security components"""
        try:
            # First ensure database is ready
            await ensure_db_initialized()
            
            # Create database tables if they don't exist
            engine = await initialize_engine()
            await create_tables(engine)
            
            # Now proceed with key initialization
            if self.auto_db_key_management:
                # Initialize database connection for key storage
                db_conn = await get_db_connection()
                self.key_repository = KeyRepository(db_conn)
                
                # Initialize keys
                await self._initialize_db_keys()
            
            return True
        except Exception as e:
            # Avoid passing exc_info=True to avoid the KeyError
            logger.error(f"Security bootstrapping failed: {e}")
            return False
    
    def _ensure_env_keys(self):
        """Ensure all security-related environment variables exist (fallback method)"""
        # Check AES_KEY
        if not os.getenv('AES_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            os.environ['AES_KEY'] = generated_key
            logger.warning(f"Generated missing AES_KEY environment variable: {generated_key[:5]}... (NOT PERSISTED)")
            
        # Check ENCRYPTION_KEY  
        if not os.getenv('ENCRYPTION_KEY'):
            generated_key = Fernet.generate_key().decode()
            os.environ['ENCRYPTION_KEY'] = generated_key
            logger.warning(f"Generated missing ENCRYPTION_KEY environment variable: {generated_key[:5]}... (NOT PERSISTED)")
            
        # Check JWT_SECRET_KEY
        if not os.getenv('JWT_SECRET_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
            os.environ['JWT_SECRET_KEY'] = generated_key
            logger.warning(f"Generated missing JWT_SECRET_KEY environment variable: {generated_key[:5]}... (NOT PERSISTED)")
    
    async def _initialize_db_keys(self):
        """Initialize database key storage and synchronize with environment"""
        if not self.key_repository:
            logger.error("Key repository not initialized")
            return False
            
        for key_name in self.KEY_TYPES:
            # Try to get key from database first
            stored_key = await self.key_repository.get_key(key_name)
            
            if stored_key:
                # Key exists in database, set it in environment
                logger.debug(f"Loaded {key_name} from database: {stored_key[:5]}...")
                os.environ[key_name] = stored_key
            else:
                # Key doesn't exist in database
                env_key = os.getenv(key_name)
                
                if env_key:
                    # Key exists in environment but not in database, store it
                    logger.info(f"Storing existing {key_name} in database")
                    await self.key_repository.store_key(key_name, env_key)
                else:
                    # Key doesn't exist anywhere, generate and store it
                    new_key = self._generate_key(key_name)
                    os.environ[key_name] = new_key
                    await self.key_repository.store_key(key_name, new_key)
                    logger.info(f"Generated and stored new {key_name}: {new_key[:5]}...")
        
        return True
    
    def _generate_key(self, key_type):
        """Generate a new key based on the key type"""
        if key_type == "AES_KEY":
            return base64.urlsafe_b64encode(os.urandom(32)).decode()
        elif key_type == "ENCRYPTION_KEY":
            return Fernet.generate_key().decode()
        elif key_type == "JWT_SECRET_KEY":
            return base64.urlsafe_b64encode(os.urandom(24)).decode()
        else:
            raise ValueError(f"Unknown key type: {key_type}")
