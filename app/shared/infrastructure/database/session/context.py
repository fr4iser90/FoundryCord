"""Database session context management."""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.shared.interface.logging.api import get_db_logger
from .factory import get_session

logger = get_db_logger()

@asynccontextmanager
async def session_context() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions.
    
    Usage:
        async with session_context() as session:
            # Use session here
            result = await session.execute(query)
    """
    async for session in get_session():
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            await session.close()
