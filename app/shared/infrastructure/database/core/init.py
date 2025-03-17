"""Database initialization and table creation."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.models.base import Base

logger = get_db_logger()

async def create_tables(engine: AsyncEngine) -> bool:
    """Create all database tables defined in the models"""
    try:
        logger.info("Checking for existing database tables...")
        
        # Connection check with retry logic
        async def check_connection(max_retries=3):
            for attempt in range(1, max_retries + 1):
                try:
                    async with engine.connect() as conn:
                        result = await conn.execute(text("SELECT 1"))
                        return True
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = 2 * attempt
                        logger.warning(f"Connection attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                        return False
            return False
            
        # Make sure we can connect before proceeding
        if not await check_connection():
            return False
        
        # First, check if tables already exist
        async with engine.connect() as conn:
            # Check if the categories table exists (as a representative table)
            result = await conn.execute(text("SELECT to_regclass('public.categories')"))
            table_exists = result.scalar() is not None
            
            if table_exists:
                logger.info("Database tables already exist, skipping creation")
                return True
        
        # If we get here, tables don't exist, so create them
        logger.info("Creating database tables...")
        
        # Import all models to make sure they're registered with the metadata
        # These imports need to be here to make sure all models are loaded
        from app.bot.infrastructure.database.models import CategoryEntity, ChannelEntity, CategoryPermissionEntity, ChannelPermissionEntity
        
        # Create tables with explicit engine connection and transaction
        async with engine.begin() as conn:
            # Create all tables defined in Base
            await conn.run_sync(Base.metadata.create_all)
            
        # Verify tables exist
        async with engine.connect() as conn:
            # Test categories table
            try:
                result = await conn.execute(text("SELECT 1 FROM categories LIMIT 1"))
                logger.info("Categories table exists and is accessible")
            except Exception as e:
                logger.error(f"Categories table verification failed: {e}")
                return False
                
            # Test channels table
            try:
                result = await conn.execute(text("SELECT 1 FROM channels LIMIT 1"))
                logger.info("Channels table exists and is accessible")
            except Exception as e:
                logger.error(f"Channels table verification failed: {e}")
                return False
        
        logger.info("All database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in database table operation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False 

async def wait_for_database(max_retries=5):
    """Wait for database to be available"""
    from sqlalchemy import text
    from app.shared.infrastructure.database.models.base import initialize_engine

    try:
        logger.info("Checking database availability...")
        engine = await initialize_engine()
        
        # Test connection with simple query
        for attempt in range(1, max_retries + 1):
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    if result.scalar() == 1:
                        logger.info("Database connection verified")
                        return True
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Database not available (attempt {attempt}/{max_retries}): {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Database not available after {max_retries} attempts: {e}")
                    return False
        
        return False
    except Exception as e:
        logger.error(f"Error checking database availability: {e}")
        return False 