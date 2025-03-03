from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from core.utilities.logger import logger

# Debug-Logging für Datenbankverbindung
logger.info("=== Database Connection Setup ===")
logger.debug("Checking environment variables:")
for key in ['APP_DB_USER', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB']:
    value = os.getenv(key)
    logger.debug(f"{key}: {'[SET]' if value else '[NOT SET]'} = {value if value else 'None'}")

# Construct database URL (ohne Passwort-Logging)
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('APP_DB_USER')}:{os.getenv('APP_DB_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Log safe version of URL (ohne Passwort)
safe_url = DATABASE_URL.replace(os.getenv('APP_DB_PASSWORD', ''), '[HIDDEN]')
logger.info(f"Attempting database connection with URL: {safe_url}")

try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # SQL-Logging deaktivieren
        pool_pre_ping=True
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    try:
        async with async_session() as session:
            logger.debug("New database session created")
            yield session
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        raise
    finally:
        logger.debug("Database session closed")
        await session.close()