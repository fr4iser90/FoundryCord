"""Database session management."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.models.base import engine

logger = get_db_logger()

# Session factory will be set during initialization
_async_session_factory = None

async def initialize_session():
    """Initialize the session factory.
    
    This must be called during application startup before any sessions
    can be created.
    
    Returns:
        The session factory
    """
    global _async_session_factory
    
    if not engine:
        raise RuntimeError("Engine must be initialized before creating session factory")
    
    _async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    logger.debug("Async session factory initialized")
    return _async_session_factory

async def get_session():
    """Get a database session directly.
    
    The caller is responsible for closing the session when done.
    
    Returns:
        An SQLAlchemy AsyncSession
    
    Raises:
        RuntimeError: If initialize_session has not been called
    """
    if not _async_session_factory:
        raise RuntimeError("Session factory must be initialized before getting a session")
    
    session = _async_session_factory()
    return session 