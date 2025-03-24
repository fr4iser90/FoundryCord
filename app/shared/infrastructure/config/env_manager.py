# app/shared/infrastructure/config/env_manager.py
import os
import logging
from typing import Dict, Any, Optional, Union
from app.shared.interface.logging.api import get_db_logger
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text, select
from app.shared.infrastructure.database.core.config import get_database_url

logger = get_db_logger()

class EnvManager:
    """
    Enhanced environment variable manager for HomeLab Discord Bot
    Supports both environment variables and database-stored configuration
    """
    
    def __init__(self):
        self.logger = logging.getLogger("homelab.env_manager")
        self.config = {}
        self._db_session = None
        self._initialized = False
    
    def configure(self) -> Dict[str, str]:
        """Load environment variables into configuration dictionary"""
        try:
            # First read environment variables as baseline configuration
            self._load_from_env()
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading environment variables: {e}")
            return {}
    
    async def configure_async(self) -> Dict[str, str]:
        """Load configuration from both environment variables and database (async version)"""
        try:
            # First load from environment variables
            self._load_from_env()
            
            # Then try to load from database, which will override env vars when available
            try:
                await self._load_from_database()
            except Exception as e:
                self.logger.warning(f"Could not load configuration from database: {e}")
                self.logger.info("Using environment variables as fallback")
            
            self._initialized = True
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error in configure_async: {e}")
            return self.config
    
    def _load_from_env(self) -> None:
        """Load all environment variables"""
        for key, value in os.environ.items():
            # Skip any development or test values
            if key.startswith(('DEV_', 'TEST_')):
                continue
                
            self.config[key] = value
            
            # Log loaded values (but hide sensitive values)
            if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                self.logger.debug(f"Loaded {key}=[HIDDEN]")
            else:
                self.logger.debug(f"Loaded {key}={value}")
    
    async def _load_from_database(self) -> None:
        """Load configuration from database"""
        if not self._db_session:
            await self._initialize_db_session()
            
        if not self._db_session:
            self.logger.warning("Could not initialize database session")
            return
            
        try:
            # Import here to avoid circular imports
            from app.shared.infrastructure.models import Config
            
            async with self._db_session() as session:
                # Get all configuration entries
                result = await session.execute(select(Config))
                configs = result.scalars().all()
                
                if not configs:
                    self.logger.info("No configuration found in database")
                    return
                    
                # Override environment variables with database values
                for config in configs:
                    # Convert value to appropriate type if possible
                    value = self._parse_value(config.value)
                    self.config[config.key] = value
                    
                    # Log loaded values (but hide sensitive values)
                    if any(sensitive in config.key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                        self.logger.debug(f"Loaded from DB: {config.key}=[HIDDEN]")
                    else:
                        self.logger.debug(f"Loaded from DB: {config.key}={value}")
                        
                self.logger.info(f"Loaded {len(configs)} configuration values from database")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration from database: {e}")
            raise
    
    async def _initialize_db_session(self) -> None:
        """Initialize the database session for config queries"""
        try:
            # Import here to avoid circular imports
            from app.shared.infrastructure.database.session.factory import get_session
            
            # Test if we can get a session
            async for test_session in get_session():
                await test_session.execute("SELECT 1")
                # If we reach here, database connection works
                break
                
            # Store the get_session function for later use
            self._db_session = get_session
            self.logger.info("Database session initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database session: {e}")
            self._db_session = None
    
    def _parse_value(self, value: str) -> Any:
        """Parse a string value into the appropriate type"""
        if not value:
            return value
            
        # Try to convert to boolean
        if value.lower() in ('true', 'yes', '1', 'y'):
            return True
        if value.lower() in ('false', 'no', '0', 'n'):
            return False
            
        # Try to convert to integer
        try:
            if value.isdigit():
                return int(value)
        except (ValueError, AttributeError):
            pass
            
        # Try to convert to float
        try:
            if value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                return float(value)
        except (ValueError, AttributeError):
            pass
            
        # Return as string if no conversion applies
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def get_bool(self, key: str) -> bool:
        """Get a boolean configuration value"""
        value = self.get(key)
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'y')
        return bool(value)
    
    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get an integer configuration value"""
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """Get a float configuration value"""
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, float):
            return value
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, separator: str = ',') -> list:
        """Get a list configuration value (comma-separated by default)"""
        value = self.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator)]
        return [value]  # Single item as list
    
    async def set(self, key: str, value: Any) -> bool:
        """Set a configuration value in both memory and database"""
        # Update in-memory value
        self.config[key] = value
        
        # Update in database if session is available
        if self._db_session:
            try:
                # Import here to avoid circular imports
                from app.shared.infrastructure.models import Config
                
                async with self._db_session() as session:
                    # Check if the key already exists
                    result = await session.execute(
                        select(Config).where(Config.key == key)
                    )
                    config = result.scalars().first()
                    
                    # Convert value to string for storage
                    str_value = str(value) if value is not None else None
                    
                    if config:
                        # Update existing entry
                        config.value = str_value
                    else:
                        # Create new entry
                        config = Config(key=key, value=str_value)
                        session.add(config)
                    
                    await session.commit()
                    return True
            except Exception as e:
                self.logger.error(f"Failed to save configuration to database: {e}")
                return False
        return True  # Return True if we at least updated the in-memory value


async def configure_database_async():
    """Configure database connection with proper retry logic (async version)"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    db_url = get_database_url()
    if not db_url:
        raise ValueError("Database URL not configured")
        
    max_retries = 5
    retry_interval = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_async_engine(db_url, echo=False)
            
            # Test connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            # Create and configure session factory
            async_session_factory = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )
            
            # Register Session for app-wide use
            from app.shared.domain.models import Base
            Base.metadata.bind = engine
            
            return engine, async_session_factory
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(retry_interval)
            else:
                raise RuntimeError(f"Failed to connect to database after {max_retries} attempts") from e