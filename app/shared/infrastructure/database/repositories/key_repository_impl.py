"""Key repository implementation for storing and retrieving encryption keys."""
import os
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.infrastructure.database.core.connection import get_config, set_config

class KeyRepository:
    """Repository for storing and retrieving encryption keys"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.initialized = False
        
    async def initialize(self):
        """Initialize the key repository"""
        # Make sure the database connection is initialized
        if not getattr(self.db_connection, 'initialized', False):
            await self.db_connection.initialize()
            
        self.initialized = True
        return True
        
    async def get_aes_key(self) -> Optional[str]:
        """Get the AES key from database"""
        try:
            query = "SELECT value FROM config WHERE key = 'security_key_AES_KEY'"
            result = await self.db_connection.execute(query)
            row = result.first()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting AES key: {e}")
            return None
        
    async def save_aes_key(self, key_value: str) -> bool:
        """Save the AES key to database"""
        try:
            async with self.db_connection.session() as session:
                # Check if key exists
                query = "SELECT value FROM config WHERE key = 'security_key_AES_KEY'"
                result = await session.execute(query)
                row = result.first()
                
                if row:
                    # Update existing
                    update_query = "UPDATE config SET value = :value WHERE key = 'security_key_AES_KEY'"
                    await session.execute(update_query, {"value": key_value})
                else:
                    # Insert new
                    insert_query = "INSERT INTO config (key, value) VALUES ('security_key_AES_KEY', :value)"
                    await session.execute(insert_query, {"value": key_value})
                    
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving AES key: {e}")
            return False
        
    async def get_jwt_secret_key(self) -> Optional[str]:
        """Get the JWT secret key from database"""
        try:
            query = "SELECT value FROM config WHERE key = 'security_key_JWT_SECRET_KEY'"
            result = await self.db_connection.execute(query)
            row = result.first()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting JWT secret key: {e}")
            return None
        
    async def save_jwt_secret_key(self, key_value: str) -> bool:
        """Save the JWT secret key to database"""
        try:
            async with self.db_connection.session() as session:
                # Check if key exists
                query = "SELECT value FROM config WHERE key = 'security_key_JWT_SECRET_KEY'"
                result = await session.execute(query)
                row = result.first()
                
                if row:
                    # Update existing
                    update_query = "UPDATE config SET value = :value WHERE key = 'security_key_JWT_SECRET_KEY'"
                    await session.execute(update_query, {"value": key_value})
                else:
                    # Insert new
                    insert_query = "INSERT INTO config (key, value) VALUES ('security_key_JWT_SECRET_KEY', :value)"
                    await session.execute(insert_query, {"value": key_value})
                    
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving JWT secret key: {e}")
            return False
        
    async def get_encryption_key(self) -> Optional[str]:
        """Get the encryption key from database"""
        try:
            query = "SELECT value FROM config WHERE key = 'security_key_ENCRYPTION_KEY'"
            result = await self.db_connection.execute(query)
            row = result.first()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting encryption key: {e}")
            return None
        
    async def save_encryption_key(self, key_value: str) -> bool:
        """Save the encryption key to database"""
        try:
            async with self.db_connection.session() as session:
                # Check if key exists
                query = "SELECT value FROM config WHERE key = 'security_key_ENCRYPTION_KEY'"
                result = await session.execute(query)
                row = result.first()
                
                if row:
                    # Update existing
                    update_query = "UPDATE config SET value = :value WHERE key = 'security_key_ENCRYPTION_KEY'"
                    await session.execute(update_query, {"value": key_value})
                else:
                    # Insert new
                    insert_query = "INSERT INTO config (key, value) VALUES ('security_key_ENCRYPTION_KEY', :value)"
                    await session.execute(insert_query, {"value": key_value})
                    
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving encryption key: {e}")
            return False
