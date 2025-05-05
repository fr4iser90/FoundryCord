"""Database configuration."""
import os
from app.shared.interfaces.logging.api import get_bot_logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

logger = get_bot_logger()

def get_database_url():
    """Get the database connection URL from environment variables.
    
    Returns:
        str: Database connection URL for SQLAlchemy
    """
    db_user = os.environ.get('APP_DB_USER')
    db_password = os.environ.get('APP_DB_PASSWORD')
    db_host = os.environ.get('POSTGRES_HOST')
    db_port = os.environ.get('POSTGRES_PORT')
    db_name = os.environ.get('POSTGRES_DB')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.warning("Missing database environment variables!")
        # Log the available variables to help find errors
        for name, value in [
            ('APP_DB_USER', db_user),
            ('POSTGRES_HOST', db_host),
            ('POSTGRES_PORT', db_port),
            ('POSTGRES_DB', db_name)
        ]:
            logger.warning(f"{name}: {value or '[NOT SET]'}")
                
    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

async def create_db_engine(url=None, max_retries=5, retry_interval=5):
    """Create a SQLAlchemy engine with connection retry logic.
    
    Args:
        url (str, optional): Database connection URL. If not provided,
            it will be obtained from environment variables.
        max_retries (int): Maximum number of connection attempts
        retry_interval (int): Seconds to wait between attempts
    
    Returns:
        The SQLAlchemy engine
        
    Raises:
        Exception: If connection fails after max_retries
    """
    if url is None:
        url = get_database_url()
    
    # Log a safe version of the URL (without password)
    safe_url = url
    password = os.environ.get('APP_DB_PASSWORD', '')
    if password:
        safe_url = url.replace(password, '[HIDDEN]')
    logger.info(f"Creating database engine with URL: {safe_url}")
    
    # Make sure SQLAlchemy is properly imported
    from sqlalchemy.ext.asyncio import create_async_engine
    
    retries = 0
    while retries < max_retries:
        try:
            engine = create_async_engine(
                url,
                echo=False,
                pool_pre_ping=True,
                future=True
            )
            
            # Test connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                
            logger.info("Database engine created successfully")
            return engine
        except Exception as e:
            retries += 1
            logger.warning(f"Database connection attempt {retries} failed: {str(e)}")
            if retries >= max_retries:
                logger.error(f"Failed to create database engine after {max_retries} attempts: {str(e)}")
                raise
            await asyncio.sleep(retry_interval)

# The rest of your code remains the same
engine = None

async def initialize_engine():
    global engine
    engine = await create_db_engine()
    return engine

async_session = None

async def initialize_session():
    global async_session, engine
    if engine is None:
        engine = await initialize_engine()
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session

async def get_session():
    global async_session
    if async_session is None:
        await initialize_session()
        
    try:
        async with async_session() as session:
            logger.debug("New database session created")
            yield session
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        raise
    finally:
        logger.debug("Database session closed")

async def get_async_session():
    """Create and return a new async session for isolated processes"""
    # Erstellt eine isolierte Session mit eigener Verbindung
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True  # Prüft, ob die Verbindung noch funktioniert
    )
    
    # Eigene Session-Factory pro Aufruf
    session_factory = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    return session_factory()