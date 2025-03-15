import asyncio
from datetime import datetime
from app.shared.infrastructure.database import get_db_connection

class KeyRepository:
    """Repository for storing and retrieving encryption keys"""
    
    def __init__(self):
        self.db = get_db_connection()
        
    async def initialize(self):
        """Initialize the key storage table if it doesn't exist"""
        query = """
        CREATE TABLE IF NOT EXISTS security_keys (
            key_name VARCHAR(50) PRIMARY KEY,
            key_value TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.db.execute(query)
        
    async def get_encryption_keys(self):
        """Get encryption keys from the database"""
        current_key = await self.db.fetch_one(
            "SELECT key_value FROM security_keys WHERE key_name = 'current_encryption_key'"
        )
        
        previous_key = await self.db.fetch_one(
            "SELECT key_value FROM security_keys WHERE key_name = 'previous_encryption_key'"
        )
        
        return {
            'current_key': current_key['key_value'] if current_key else None,
            'previous_key': previous_key['key_value'] if previous_key else None
        }
        
    async def save_encryption_keys(self, current_key, previous_key):
        """Save encryption keys to database"""
        # First save current key
        await self.db.execute(
            """
            INSERT INTO security_keys (key_name, key_value, updated_at)
            VALUES ('current_encryption_key', :current_key, :timestamp)
            ON CONFLICT (key_name) 
            DO UPDATE SET key_value = :current_key, updated_at = :timestamp
            """,
            {"current_key": current_key, "timestamp": datetime.now()}  # Use a dictionary instead of a tuple
        )
        
        # Then save previous key if it exists
        if previous_key:
            await self.db.execute(
                """
                INSERT INTO security_keys (key_name, key_value, updated_at)
                VALUES ('previous_encryption_key', :previous_key, :timestamp)
                ON CONFLICT (key_name) 
                DO UPDATE SET key_value = :previous_key, updated_at = :timestamp
                """,
                {"previous_key": previous_key, "timestamp": datetime.now()}  # Use a dictionary instead of a tuple
            )
            
    async def get_aes_key(self):
        """Get the AES key"""
        result = await self.db.fetch_one(
            "SELECT key_value FROM security_keys WHERE key_name = 'aes_key'"
        )
        return result['key_value'] if result else None
        
    async def save_aes_key(self, aes_key):
        """Save AES key to database"""
        await self.db.execute(
            """
            INSERT INTO security_keys (key_name, key_value, updated_at)
            VALUES ('aes_key', :aes_key, :timestamp)
            ON CONFLICT (key_name) 
            DO UPDATE SET key_value = :aes_key, updated_at = :timestamp
            """,
            {"aes_key": aes_key, "timestamp": datetime.now()}
        )
        
    async def get_jwt_secret_key(self):
        """Get the JWT secret key"""
        result = await self.db.fetch_one(
            "SELECT key_value FROM security_keys WHERE key_name = 'jwt_secret_key'"
        )
        return result['key_value'] if result else None
        
    async def save_jwt_secret_key(self, jwt_secret_key):
        """Save JWT secret key to database"""
        await self.db.execute(
            """
            INSERT INTO security_keys (key_name, key_value, updated_at)
            VALUES ('jwt_secret_key', :jwt_secret_key, :timestamp)
            ON CONFLICT (key_name) 
            DO UPDATE SET key_value = :jwt_secret_key, updated_at = :timestamp
            """,
            {"jwt_secret_key": jwt_secret_key, "timestamp": datetime.now()}
        )
    
    async def get_last_rotation_time(self):
        """Get the timestamp of the last key rotation"""
        result = await self.db.fetch_one(
            "SELECT updated_at FROM security_keys WHERE key_name = 'current_encryption_key'"
        )
        return result['updated_at'] if result else None
        
    async def save_rotation_timestamp(self, timestamp):
        """Save timestamp of last key rotation to database"""
        await self.db.execute(
            """
            INSERT INTO security_keys (key_name, key_value, updated_at)
            VALUES ('last_key_rotation', :timestamp_str, :timestamp)
            ON CONFLICT (key_name) 
            DO UPDATE SET key_value = :timestamp_str, updated_at = :timestamp
            """,
            {"timestamp_str": timestamp.isoformat(), "timestamp": timestamp}
        )
