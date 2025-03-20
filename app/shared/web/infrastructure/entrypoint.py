"""Web application entrypoint."""
import asyncio
import traceback

from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.bootstrapper import initialize_database

logger = get_web_logger()

async def start_web():
    """Start the web application with proper separation of concerns."""
    try:
        logger.info("Starting web application")
        
        # Initialisiere die Datenbank mit dem zentralen Bootstrapper
        if not await initialize_database():
            logger.error("Failed to initialize database")
            return False
            
        # Start web server here
        logger.info("Web application started successfully")
        return True
        
    except Exception as e:
        # Enhanced exception logging
        error_details = str(e)
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(f"Failed to start web application: {error_details}")
        logger.error(f"Exception type: {error_type}")
        logger.error(f"Stack trace: \n{stack_trace}")
        return False

if __name__ == "__main__":
    asyncio.run(start_web())
