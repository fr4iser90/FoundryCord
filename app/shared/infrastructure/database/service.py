"""
Database service for managing database sessions and connections.
"""
from typing import Optional, Callable, ContextManager
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

from app.shared.interface.logging.api import get_db_logger
logger = get_db_logger()

class DatabaseService:
    """Service for managing database connections and sessions"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the database service"""
        from app.shared.infrastructure.database.core.connection import get_database_connection_string
        
        if connection_string is None:
            connection_string = get_database_connection_string()
            
        self.connection_string = connection_string
        self.engine = create_async_engine(connection_string, echo=False, poolclass=NullPool)
        self._async_session_factory = sessionmaker(
            bind=self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        # Create sync engine for compatibility
        self._sync_engine = create_engine(
            connection_string.replace('+asyncpg', ''),
            echo=False, 
            poolclass=NullPool
        )
        self._session_factory = sessionmaker(
            bind=self._sync_engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        logger.info(f"DatabaseService initialized with connection string: {self._mask_connection_string(connection_string)}")
        
    def _mask_connection_string(self, conn_string: str) -> str:
        """Mask sensitive information in the connection string"""
        if "://" not in conn_string:
            return "[INVALID CONNECTION STRING]"
            
        prefix, rest = conn_string.split("://", 1)
        if "@" not in rest:
            return f"{prefix}://[MASKED]"
            
        auth, host_info = rest.split("@", 1)
        if ":" in auth:
            username, _ = auth.split(":", 1)
            return f"{prefix}://{username}:[HIDDEN]@{host_info}"
            
        return f"{prefix}://{auth}@{host_info}"
        
    @contextmanager
    def session(self) -> ContextManager[Session]:
        """Get a database session context manager"""
        session = self._session_factory()
        try:
            yield session
        except Exception as e:
            logger.error(f"Error in database session: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            
    async def async_session(self) -> AsyncSession:
        """Get an async database session"""
        return self._async_session_factory()
        
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        self._sync_engine.dispose()
        logger.info("Database connections closed")
        
    def get_engine(self):
        """Get the SQLAlchemy engine"""
        return self.engine
        
    def get_sync_engine(self):
        """Get the synchronous SQLAlchemy engine"""
        return self._sync_engine 