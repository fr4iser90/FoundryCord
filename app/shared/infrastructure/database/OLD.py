"""Database initialization module."""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Create a global flag to track initialization
_INITIALIZED = False
_ENGINE = None
_SESSION = None

logger = logging.getLogger(__name__)

def init_database(connection_string: str, echo: bool = False):
    """Initialize the database connection.
    
    This function should only be called once during application startup.
    """
    global _INITIALIZED, _ENGINE, _SESSION
    
    if _INITIALIZED:
        logger.warning("Database already initialized. Skipping.")
        return _ENGINE, _SESSION
        
    logger.info(f"Initializing database with connection string: {connection_string}")
    
    # Create engine and session
    _ENGINE = create_engine(connection_string, echo=echo)
    _SESSION = sessionmaker(bind=_ENGINE)
    
    # Mark as initialized
    _INITIALIZED = True
    
    return _ENGINE, _SESSION

async def init_async_database(connection_string: str, echo: bool = False):
    """Initialize the async database connection."""
    global _INITIALIZED, _ENGINE, _SESSION
    
    if _INITIALIZED:
        logger.warning("Async database already initialized. Skipping.")
        return _ENGINE, _SESSION
        
    logger.info(f"Initializing async database with connection string: {connection_string}")
    
    # Create async engine and session
    _ENGINE = create_async_engine(connection_string, echo=echo)
    _SESSION = sessionmaker(bind=_ENGINE, class_=AsyncSession)
    
    # Mark as initialized
    _INITIALIZED = True
    
    return _ENGINE, _SESSION 