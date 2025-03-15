import os
import base64
from cryptography.fernet import Fernet
from app.shared.logging import logger
from app.shared.infrastructure.database.repositories.key_repository_impl import KeyRepository

class SecurityBootstrapper:
    """Handles security initialization and key bootstrapping"""
    
    def __init__(self, auto_db_key_management=True):
        self.auto_db_key_management = auto_db_key_management
        self.key_repository = KeyRepository()
        
    async def initialize(self):
        """Initialize security components"""
        await self.key_repository.initialize()
        
        # Setup environment variables if needed
        self._ensure_env_keys()
        
        # Setup database keys if using automatic key management
        if self.auto_db_key_management:
            await self._ensure_db_keys()
            
        logger.info("Security bootstrapping completed")
    
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
    
    async def _ensure_db_keys(self):
        """Ensure all security keys are stored in the database"""
        # Handle AES key
        aes_key = await self.key_repository.get_aes_key()
        if not aes_key:
            aes_key = os.getenv('AES_KEY')
            await self.key_repository.save_aes_key(aes_key)
            logger.info("Saved AES key to database")
        
        # Handle JWT secret key
        jwt_key = await self.key_repository.get_jwt_secret_key()
        if not jwt_key:
            jwt_key = os.getenv('JWT_SECRET_KEY')
            await self.key_repository.save_jwt_secret_key(jwt_key)
            logger.info("Saved JWT secret key to database")
        
        # Handle encryption keys
        keys = await self.key_repository.get_encryption_keys()
        if not keys or not keys.get('current_key'):
            current_key = os.getenv('ENCRYPTION_KEY')
            await self.key_repository.save_encryption_keys(current_key, None)
            logger.info("Saved encryption key to database")
