"""Bot application entrypoint."""
import logging
import asyncio
from sqlalchemy import text

from app.shared.infrastructure.startup.bootstrap import ApplicationBootstrap
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres
from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

async def verify_database():
    """Verify that required data exists."""
    try:
        # Wait for database
        if not await wait_for_postgres():
            logger.error("Database not available")
            return False

        # Check if required tables have data
        async with session_context() as session:
            tables = ['categories', 'channels', 'dashboards']
            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                if count == 0:
                    logger.error(f"No data found in {table}. Please initialize database from web interface")
                    return False
                    
            logger.info("Database verification successful")
            return True
            
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

async def start_bot():
    """Start the bot application."""
    try:
        # Initialize application
        bootstrap = ApplicationBootstrap(container_type="bot")
        if not await bootstrap.bootstrap():
            logger.error("Failed to bootstrap bot application")
            return False
            
        # Verify database has required data
        if not await verify_database():
            logger.error("Database verification failed")
            return False
            
        # Start bot here
        logger.info("Bot application started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start bot application: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(start_bot())