# app/shared/infrastructure/config/env_manager.py
import os
import logging
from typing import Dict, Any, Optional
from app.shared.interface.logging.api import get_db_logger
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.shared.infrastructure.database.core.config import get_database_url
import asyncio
from sqlalchemy.sql import text

logger = get_db_logger()

class EnvManager:
    """
    Simple environment variable manager for HomeLab Discord Bot
    """
    
    def __init__(self):
        self.logger = logging.getLogger("homelab.env_manager")
        self.config = {}
    
    def configure(self) -> Dict[str, str]:
        """Load environment variables into configuration dictionary"""
        try:
            # Read environment variables directly
            self._load_from_env()
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading environment variables: {e}")
            return {}
    
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
    
    def get(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        return self.config.get(key)
    
    def get_bool(self, key: str) -> bool:
        """Get a boolean configuration value"""
        value = self.get(key)
        if not value:
            return False
        return value.lower() in ('true', 'yes', '1', 'y')
    
    def get_int(self, key: str) -> Optional[int]:
        """Get an integer configuration value"""
        value = self.get(key)
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_list(self, key: str, separator: str = ',') -> list:
        """Get a list configuration value (comma-separated by default)"""
        value = self.get(key)
        if not value:
            return []
        return [item.strip() for item in value.split(separator)]

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