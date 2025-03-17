"""Context managers for database sessions."""
from contextlib import asynccontextmanager
from app.shared.interface.logging.api import get_db_logger
from .factory import get_session

logger = get_db_logger()

@asynccontextmanager
async def session_context():
    """Get a database session as a context manager.
    
    This automatically closes the session when exiting the context.
    
    Example:
        async with session_context() as session:
            result = await session.execute(query)
    """
    session = await get_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Session error: {str(e)}")
        raise
    finally:
        await session.close()
