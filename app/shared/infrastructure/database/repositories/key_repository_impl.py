from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.models import Config
from typing import Optional
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class KeyRepository:
    """Repository for managing security keys in the database"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def ensure_table_exists(self) -> bool:
        """Ensure the security_keys table exists"""
        # This should be handled by SQLAlchemy migrations or Base.metadata.create_all
        # Not in the repository itself
        return True
    
    async def get_key(self, key_name: str) -> Optional[str]:
        """Get a key from the database by name"""
        try:
            result = await self.session.execute(
                select(Config).where(Config.key == key_name)
            )
            config = result.scalar_one_or_none()
            return config.value if config else None
        except Exception as e:
            # Handle the case where the table doesn't exist yet
            if "relation" in str(e) and "does not exist" in str(e):
                logger.warning(f"Config table does not exist yet, returning None for key {key_name}")
                return None
            else:
                # Re-raise other exceptions
                raise
    
    async def store_key(self, key_name: str, key_value: str) -> bool:
        """Store a key in the database"""
        # Check if key exists
        result = await self.session.execute(
            select(Config).where(Config.key == key_name)
        )
        config = result.scalar_one_or_none()
        
        if config:
            # Update existing key
            config.value = key_value
        else:
            # Create new key
            config = Config(key=key_name, value=key_value)
            self.session.add(config)
            
        try:
            await self.session.commit()
            logger.debug(f"Stored key {key_name} in database")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to store key {key_name}: {e}")
            return False