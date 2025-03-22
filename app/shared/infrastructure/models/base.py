"""Base model for SQLAlchemy ORM."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Create declarative base
Base = declarative_base()

# Engine will be set during initialization
engine = None
_async_session_factory = None
_initialized = False

async def initialize_engine(connection_string=None):
    """Initialize the database engine with the given connection string."""
    global engine, _initialized
    
    if not connection_string:
        connection_string = _build_connection_string()
    
    logger.info(f"Initializing database engine with connection string")
    
    try:
        engine = create_async_engine(
            connection_string,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _initialized = True
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        raise

async def initialize_session():
    """Initialize the session factory."""
    global _async_session_factory
    
    if not engine:
        raise RuntimeError("Engine must be initialized before creating session factory")
    
    try:
        _async_session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        logger.debug("Async session factory initialized")
        return _async_session_factory
    except Exception as e:
        logger.error(f"Failed to initialize session factory: {e}")
        raise

async def get_direct_session():
    """Get a direct session object - not a context manager."""
    global _async_session_factory, engine
    
    if not _async_session_factory:
        if not engine:
            await initialize_engine()
        await initialize_session()
    
    return _async_session_factory()

async def initialize_tables():
    """Create all tables defined in the models."""
    global engine
    
    if not engine:
        await initialize_engine()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def _build_connection_string():
    """Build a database connection string from environment variables."""
    user = os.getenv("APP_DB_USER", "homelab_discord_bot")
    password = os.getenv("APP_DB_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "homelab-postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "homelab")
    
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
