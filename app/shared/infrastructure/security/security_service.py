"""Security service for web application."""
import logging
from typing import Optional, Dict, Any
from app.shared.infrastructure.security.security_bootstrapper import SecurityBootstrapper

logger = logging.getLogger("homelab.bot")

class SecurityService:
    """Service for managing security features."""
    
    def __init__(self):
        """Initialize the security service."""
        self.security_bootstrapper = SecurityBootstrapper()
        self.keys = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize security service."""
        if self.initialized:
            logger.debug("Security service already initialized")
            return True
            
        try:
            # Initialize security bootstrapper
            if not await self.security_bootstrapper.initialize():
                logger.error("Failed to initialize security bootstrapper")
                return False
            
            # Load keys from bootstrapper
            for key_type in self.security_bootstrapper.KEY_TYPES:
                self.keys[key_type] = self.security_bootstrapper.get_key(key_type)
            
            # Validate that all required keys are available
            missing_keys = [k for k, v in self.keys.items() if not v]
            if missing_keys:
                logger.error(f"Missing security keys: {', '.join(missing_keys)}")
                return False
                
            self.initialized = True
            logger.info("Security service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security service: {str(e)}")
            return False
    
    def get_key(self, key_name: str) -> Optional[str]:
        """Get a security key by name."""
        if not self.initialized:
            raise RuntimeError("Security service not initialized")
        return self.keys.get(key_name)
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its payload."""
        if not self.initialized:
            raise RuntimeError("Security service not initialized")
            
        try:
            from jose import jwt
            key = self.get_key('JWT_SECRET_KEY')
            if not key:
                raise ValueError("JWT secret key not available")
                
            payload = jwt.decode(token, key, algorithms=['HS256'])
            return {"valid": True, "payload": payload}
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": str(e)}