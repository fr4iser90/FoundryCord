"""Database session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.core.config import get_database_url
from typing import AsyncGenerator

logger = get_db_logger()

class SessionFactory:
    """Factory for creating database sessions."""
    
    def __init__(self):
        """Initialize the session factory."""
        self._engine = None
        self._async_session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the session factory with database connection."""
        if self._initialized:
            logger.debug("Session factory already initialized")
            return True
            
        try:
            # Create engine
            database_url = get_database_url()
            # Log the URL being used
            logger.info(f"Attempting to initialize SessionFactory with database URL: {database_url}") 
            self._engine = create_async_engine(
                database_url,
                echo=False,
                future=True,
                pool_pre_ping=True
            )
            
            # Create session factory
            self._async_session_factory = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self._engine.begin() as conn:
                await conn.run_sync(lambda _: None)
            
            self._initialized = True
            logger.info("Session factory initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize session factory: {e}")
            self._initialized = False
            return False
    
    def is_initialized(self) -> bool:
        """Check if the session factory is properly initialized."""
        return self._initialized and self._engine is not None and self._async_session_factory is not None
    
    async def create_session(self) -> AsyncSession:
        """Create a new database session."""
        if not self.is_initialized():
            raise RuntimeError("Session factory must be initialized before creating sessions")
        return self._async_session_factory()
    
    async def close(self):
        """Close the session factory and its engine."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        self._async_session_factory = None
        self._initialized = False

# Global instance
_session_factory = SessionFactory()

async def initialize_session() -> bool:
    """Initialize the global session factory."""
    return await _session_factory.initialize()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session from the global factory with proper commit/rollback."""
    if not _session_factory.is_initialized():
        await initialize_session()
    
    session = await _session_factory.create_session()
    try:
        yield session
        await session.commit()
        logger.debug("Session committed successfully.")
    except Exception as e:
        logger.error(f"Exception occurred during session: {e}. Rolling back.", exc_info=True)
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("Session closed.") 