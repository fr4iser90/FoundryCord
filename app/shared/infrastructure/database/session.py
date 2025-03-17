"""Database session management."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.infrastructure.database.models.base import engine

# Session factory will be set during initialization
_async_session_factory = None

async def initialize_session():
    """Initialize the session factory."""
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

# Direct session getter (not a context manager)
async def get_session():
    """Get a database session directly."""
    if not _async_session_factory:
        raise RuntimeError("Session factory must be initialized before getting a session")
    
    return _async_session_factory()

# Context manager version
@asynccontextmanager
async def session_context():
    """Get a database session as a context manager."""
    if not _async_session_factory:
        raise RuntimeError("Session factory must be initialized before getting a session")
    
    session = _async_session_factory()
    try:
        yield session
    finally:
        await session.close() 