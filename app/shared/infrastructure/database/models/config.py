from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text  # Add this import
import os
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
import asyncio

# Debug logging for database connection
logger.info("=== Database Connection Setup ===")

# Read environment variables directly
env_vars = {
    'APP_DB_USER': os.environ.get('APP_DB_USER'),
    'APP_DB_PASSWORD': os.environ.get('APP_DB_PASSWORD'),
    'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
    'POSTGRES_PORT': os.environ.get('POSTGRES_PORT'),
    'POSTGRES_DB': os.environ.get('POSTGRES_DB')
}

# Output environment variables (without sensitive data)
logger.info("Environment variables for database connection:")
for key, value in env_vars.items():
    if 'PASSWORD' not in key:
        logger.info(f"{key}: {value if value else '[NOT SET]'}")

# Construct database URL
DATABASE_URL = f"postgresql+asyncpg://{env_vars['APP_DB_USER']}:{env_vars['APP_DB_PASSWORD']}@{env_vars['POSTGRES_HOST']}:{env_vars['POSTGRES_PORT']}/{env_vars['POSTGRES_DB']}"

# Log safe version of URL (without password)
safe_url = DATABASE_URL.replace(env_vars['APP_DB_PASSWORD'] or "", '[HIDDEN]')
logger.info(f"Attempting database connection with URL: {safe_url}")

# Add retry logic for database connection
async def create_db_engine(max_retries=5, retry_interval=5):
    retries = 0
    while retries < max_retries:
        try:
            engine = create_async_engine(
                DATABASE_URL,
                echo=False,
                pool_pre_ping=True
            )
            
            # Test connection - THIS IS THE CHANGE
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
    # Creates an isolated session with its own connection
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True  # Checks if the connection is still working
    )
    
    # Custom session factory per call
    session_factory = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    return session_factory()