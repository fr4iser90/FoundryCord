"""Bot application entrypoint."""
import asyncio
import traceback
import sys
from app.shared.interfaces.logging.api import get_bot_logger
from app.shared.infrastructure.startup.bootstrap import ApplicationBootstrap

logger = get_bot_logger()

async def start_bot():
    """Start the bot application."""
    try:
        logger.debug("Starting bot application initialization")
        
        # Create and run bootstrap
        bootstrap = ApplicationBootstrap(container_type="bot")
        if not await bootstrap.bootstrap():
            logger.error("Failed to bootstrap bot application - shutting down")
            return False
            
        logger.debug("Bot application bootstrap completed successfully")
        
        # Import and run main after successful bootstrap
        try:
            from app.bot.infrastructure.startup.main import main
            await main()
            return True
        except ImportError as ie:
            logger.error(f"Failed to import bot application main module: {ie}")
            return False
        except Exception as e:
            logger.error(f"Error running bot application main: {e}")
            return False
            
    except Exception as e:
        error_details = str(e)
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        logger.error(f"Critical error starting bot application: {error_details}")
        logger.error(f"Exception type: {error_type}")
        logger.error(f"Stack trace: \n{stack_trace}")
        return False

if __name__ == "__main__":
    success = asyncio.run(start_bot())
    sys.exit(0 if success else 1)