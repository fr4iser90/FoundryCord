from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import base64
import os
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.repositories.auth.key_repository_impl import KeyRepositoryImpl
from app.shared.infrastructure.database.session.factory import get_session
from typing import Optional, Callable, AsyncGenerator

class KeyManagementService:
    def __init__(self, session_factory: Optional[Callable[[], AsyncGenerator]] = None):
        self.current_key = None
        self.previous_key = None
        self.aes_key = None
        self.jwt_secret_key = None
        self.last_rotation = None
        self.rotation_interval = timedelta(days=30)
        self.session = None
        self.key_repository = None
        self.jwt_secret = None
        self.encryption_key = None
        self.initialized = False
        self.session_factory = session_factory or get_session
    
    async def initialize(self):
        """Initialize the key management service, generating keys if not found."""
        logger.info("[KMS] Attempting to initialize KeyManagementService...")
        # Reset initialized flag at the start of initialization attempt
        self.initialized = False 
        
        try:
            logger.info("[KMS] Getting session factory...")
            session_gen = self.session_factory()
            logger.info(f"[KMS] Obtained session generator: {session_gen}")
            
            async for session in session_gen:
                logger.info(f"[KMS] Obtained session: {session} (Active: {session.is_active if session else 'N/A'})")
                if not session or not session.is_active:
                    logger.error("[KMS] Invalid or inactive session obtained. Cannot proceed.")
                    return False # Cannot initialize without a valid session
                    
                # Initialize key repository with session
                self.key_repository = KeyRepositoryImpl(session)
                logger.info(f"[KMS] KeyRepositoryImpl initialized with session.")

                # --- Load or Generate JWT Secret Key ---
                logger.info("[KMS] Attempting to load JWT secret key...")
                self.jwt_secret = await self.key_repository.get_jwt_secret_key()

                if not self.jwt_secret:
                    logger.warning("[KMS] JWT secret key not found in database. Generating a new one...")
                    try:
                        new_jwt_secret = base64.urlsafe_b64encode(os.urandom(24)).decode()
                        await self.key_repository.save_jwt_secret_key(new_jwt_secret)
                        self.jwt_secret = new_jwt_secret # Use the newly generated key
                        logger.info("[KMS] Successfully generated and saved new JWT secret key.")
                    except Exception as gen_exc:
                        logger.error(f"[KMS] Failed to generate or save new JWT secret key: {gen_exc}")
                        # Continue to check encryption key, but initialization will likely fail overall
                else:
                     logger.info(f"[KMS] JWT secret key loaded from DB: {'********'}")

                # --- Load or Generate Encryption Key ---
                logger.info("[KMS] Attempting to load encryption key...")
                self.encryption_key = await self.key_repository.get_encryption_key()

                if not self.encryption_key:
                    logger.warning("[KMS] Encryption key not found in database. Generating a new one...")
                    try:
                        new_encryption_key = Fernet.generate_key().decode()
                        await self.key_repository.save_encryption_keys(new_encryption_key, None)
                        self.encryption_key = new_encryption_key # Use the newly generated key
                        logger.info("[KMS] Successfully generated and saved new encryption key.")
                    except Exception as gen_exc:
                         logger.error(f"[KMS] Failed to generate or save new encryption key: {gen_exc}")
                         # If this fails, initialization should likely fail overall
                else:
                    logger.info(f"[KMS] Encryption key loaded from DB: {'********'}")

                # --- Final Verification ---
                if not self.jwt_secret or not self.encryption_key:
                    logger.critical("[KMS] CRITICAL: One or more keys are still missing after load/generation attempts. Initialization failed.")
                    # Keep self.initialized = False
                    return False # Indicate failure clearly
                
                # If we reach here, both keys are available (either loaded or generated)
                self.initialized = True
                logger.info("[KMS] KeyManagementService initialized successfully (keys loaded or generated).")
                return True # Indicate success

            # If the loop finishes without yielding a session (shouldn't happen with factory pattern)
            logger.error("[KMS] Session factory did not yield a session.")
            return False

        except Exception as e:
            logger.error(f"[KMS] Unexpected error during KeyManagementService initialization: {e}")
            logger.exception("[KMS] Exception details:", exc_info=e)
            # Ensure initialized is False on any exception
            self.initialized = False 
            return False
        finally:
             # Log final state, initialized flag should be correctly set by return paths
            logger.info(f"[KMS] Exiting initialize method. Final Initialized flag: {self.initialized}")
        
    async def _load_keys(self):
        """Load keys from database, generating if needed"""
        if not self.key_repository:
            logger.error("Key repository not initialized")
            return False
            
        try:
            session_gen = self.session_factory()
            async for session in session_gen:
                self.key_repository = KeyRepositoryImpl(session)
                
                # Get encryption keys
                keys = await self.key_repository.get_encryption_keys()
                
                # If no keys exist, generate initial keys
                if not keys or not keys.get('current_key'):
                    logger.info("No encryption keys found in database. Generating initial keys.")
                    self.current_key = Fernet.generate_key().decode()
                    self.previous_key = None
                    # Save the initial key
                    await self.key_repository.save_encryption_keys(self.current_key, None)
                else:
                    self.current_key = keys.get('current_key')
                    self.previous_key = keys.get('previous_key')
                    
                # Get AES key
                self.aes_key = await self.key_repository.get_aes_key()
                if not self.aes_key:
                    logger.info("No AES key found in database. Generating initial key.")
                    self.aes_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
                    # Save the initial key
                    await self.key_repository.save_aes_key(self.aes_key)
                    
                # Get JWT secret key
                self.jwt_secret_key = await self.key_repository.get_jwt_secret_key()
                if not self.jwt_secret_key:
                    logger.info("No JWT secret key found in database. Generating initial key.")
                    self.jwt_secret_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
                    # Save the initial key
                    await self.key_repository.save_jwt_secret_key(self.jwt_secret_key)
                    
                self.last_rotation = await self._get_last_rotation_time()
                return True
                
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            return False
        
    async def _get_last_rotation_time(self):
        """Get timestamp of last key rotation from app.bot.database"""
        return await self.key_repository.get_last_rotation_time()
        
    async def needs_rotation(self):
        """Check if keys need rotation based on time interval"""
        if not self.last_rotation:
            return True
        return datetime.now() - self.last_rotation > self.rotation_interval
        
    async def rotate_keys(self):
        """Perform key rotation and store new keys in database"""
        try:
            session_gen = self.session_factory()
            async for session in session_gen:
                self.key_repository = KeyRepositoryImpl(session)
                
                self.previous_key = self.current_key
                self.current_key = Fernet.generate_key().decode()
                self.last_rotation = datetime.now()
                
                # Store keys in database ONLY
                await self.key_repository.save_encryption_keys(self.current_key, self.previous_key)
                await self.key_repository.save_rotation_timestamp(self.last_rotation)
                
                # Also rotate JWT secret key
                self.jwt_secret_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
                await self.key_repository.save_jwt_secret_key(self.jwt_secret_key)
                
                # Log key rotation (without exposing keys)
                logger.info(f"Security keys have been rotated successfully at {self.last_rotation}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rotate keys: {e}")
            return False
        
    def get_current_key(self):
        """Get the current encryption key"""
        return self.current_key
        
    def get_previous_key(self):
        """Get the previous encryption key"""
        return self.previous_key
        
    def get_aes_key(self):
        """Get the AES key"""
        return self.aes_key
        
    async def get_jwt_secret_key(self) -> Optional[str]:
        """Get JWT secret key"""
        if not self.initialized:
            await self.initialize()
        return self.jwt_secret

    async def get_encryption_key(self) -> Optional[str]:
        """Get encryption key"""
        if not self.initialized:
            await self.initialize()
        return self.encryption_key 