from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.models import Config
from typing import Optional, Dict, Any
from app.shared.interface.logging.api import get_bot_logger
import logging
import json
from datetime import datetime

logger = logging.getLogger("homelab.bot")

class KeyRepository:
    """Repository for managing security keys in the database"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def initialize(self) -> bool:
        """Initialize the repository, creating tables if needed."""
        try:
            # Create security_keys table if it doesn't exist
            await self.session.execute(text("""
                CREATE TABLE IF NOT EXISTS security_keys (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            await self.session.commit()
            logger.debug("Security keys table initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize key repository: {e}")
            await self.session.rollback()
            return False
    
    async def get_key(self, key_name: str) -> Optional[str]:
        """Get a security key from the database."""
        try:
            result = await self.session.execute(
                text("SELECT value FROM security_keys WHERE name = :name"),
                {"name": key_name}
            )
            key_value = result.scalar()
            
            if key_value:
                logger.debug(f"Retrieved security key '{key_name}' from database")
            else:
                logger.debug(f"Security key '{key_name}' not found in database")
                
            return key_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve security key '{key_name}': {e}")
            return None
    
    async def store_key(self, key_name: str, key_value: str) -> bool:
        """Store a security key in the database."""
        try:
            # Check if key already exists
            result = await self.session.execute(
                text("SELECT value FROM security_keys WHERE name = :name"),
                {"name": key_name}
            )
            existing_key = result.scalar()
            
            if existing_key:
                # Update existing key
                await self.session.execute(
                    text("UPDATE security_keys SET value = :value, updated_at = CURRENT_TIMESTAMP WHERE name = :name"),
                    {"name": key_name, "value": key_value}
                )
            else:
                # Insert new key
                await self.session.execute(
                    text("INSERT INTO security_keys (name, value) VALUES (:name, :value)"),
                    {"name": key_name, "value": key_value}
                )
            
            await self.session.commit()
            logger.info(f"Security key '{key_name}' stored successfully")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to store security key '{key_name}': {e}")
            return False
    
    # Database credential specific methods
    
    async def get_db_credentials(self) -> Optional[Dict[str, Any]]:
        """Get database credentials from secure storage."""
        try:
            credentials_json = await self.get_key('db_credentials')
            if credentials_json:
                return json.loads(credentials_json)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve database credentials: {e}")
            return None
    
    async def store_db_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Store database credentials in secure storage."""
        try:
            credentials_json = json.dumps(credentials)
            return await self.store_key('db_credentials', credentials_json)
        except Exception as e:
            logger.error(f"Failed to store database credentials: {e}")
            return False
    
    # Encryption key methods
    
    async def get_encryption_keys(self) -> Optional[Dict[str, str]]:
        """Get encryption keys from database."""
        try:
            current_key = await self.get_key('current_encryption_key')
            previous_key = await self.get_key('previous_encryption_key')
            
            return {
                'current_key': current_key,
                'previous_key': previous_key
            }
        except Exception as e:
            logger.error(f"Failed to retrieve encryption keys: {e}")
            return None
    
    async def save_encryption_keys(self, current_key: str, previous_key: Optional[str]) -> bool:
        """Save encryption keys to database."""
        try:
            # Store current key
            await self.store_key('current_encryption_key', current_key)
            
            # Store previous key if provided
            if previous_key:
                await self.store_key('previous_encryption_key', previous_key)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save encryption keys: {e}")
            return False
    
    async def get_last_rotation_time(self) -> Optional[datetime]:
        """Get the timestamp of last key rotation."""
        try:
            timestamp_str = await self.get_key('last_key_rotation')
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            return None
        except Exception as e:
            logger.error(f"Failed to get last rotation time: {e}")
            return None
    
    async def save_rotation_timestamp(self, timestamp: datetime) -> bool:
        """Save the timestamp of a key rotation."""
        try:
            timestamp_str = timestamp.isoformat()
            return await self.store_key('last_key_rotation', timestamp_str)
        except Exception as e:
            logger.error(f"Failed to save rotation timestamp: {e}")
            return False
    
    # Additional key methods for JWT, AES, etc.
    
    async def get_jwt_secret_key(self) -> Optional[str]:
        """Get JWT secret key from database."""
        return await self.get_key('jwt_secret_key')
    
    async def save_jwt_secret_key(self, key: str) -> bool:
        """Save JWT secret key to database."""
        return await self.store_key('jwt_secret_key', key)
    
    async def get_aes_key(self) -> Optional[str]:
        """Get AES key from database."""
        return await self.get_key('aes_key')
    
    async def save_aes_key(self, key: str) -> bool:
        """Save AES key to database."""
        return await self.store_key('aes_key', key)