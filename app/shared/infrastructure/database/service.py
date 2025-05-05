"""
Database service for managing database sessions and connections.
"""
from typing import Optional, Callable, ContextManager
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

from app.shared.interfaces.logging.api import get_db_logger
from app.shared.infrastructure.database.session.factory import get_session, initialize_session
from app.shared.infrastructure.database.core.config import get_database_url
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres

logger = get_db_logger()

class DatabaseService:
    """Service for managing database connections and sessions"""
    
    def __init__(self):
        """Initialize the database service."""
        self._initialized = False
        self._engine: Optional[AsyncEngine] = None
        self._session_factory = None
    
    async def initialize(self) -> bool:
        """Initialize database connections and session factory."""
        try:
            if self._initialized:
                return True

            # First wait for PostgreSQL to be available
            logger.debug("Waiting for PostgreSQL to be available...")
            if not await wait_for_postgres():
                logger.error("PostgreSQL is not available after maximum retries")
                return False

            # Create engine
            database_url = get_database_url()
            if not database_url:
                logger.error("No database URL available")
                return False
                
            self._engine = create_async_engine(
                database_url,
                echo=False,
                future=True,
                pool_pre_ping=True
            )
            
            # Test connection
            async with self._engine.begin() as conn:
                await conn.run_sync(lambda _: None)
            
            self._initialized = True
            logger.debug("Database service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            return False
    
    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        if not self._initialized:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize database service")
        async for session in get_session():
            return session
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized and self._engine is not None
    
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
    
    async def close(self):
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        self._initialized = False
        logger.debug("Database connections closed")
    
    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get the SQLAlchemy engine."""
        if not self._initialized:
            logger.error("Attempted to access engine before initialization")
            return None
        return self._engine
    
    def get_engine(self) -> Optional[AsyncEngine]:
        """Get the SQLAlchemy engine (method form for backward compatibility)."""
        return self.engine
    
    async def ensure_initialized(self) -> bool:
        """Ensure the service is initialized."""
        if not self._initialized:
            return await self.initialize()
        return True

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