"""Web application entrypoint."""
import asyncio
import traceback
import sys

from app.shared.interfaces.logging.api import get_web_logger
from app.shared.infrastructure.startup.bootstrap import ApplicationBootstrap

logger = get_web_logger()

async def start_web():
    """Start the web application."""
    try:
        logger.info("Starting web application initialization")
        
        # Create and run bootstrap
        bootstrap = ApplicationBootstrap(container_type="web")
        if not await bootstrap.bootstrap():
            logger.error("Failed to bootstrap web application - shutting down")
            return False
            
        logger.info("Web application bootstrap completed successfully")
        
        # Import and run main after successful bootstrap
        try:
            from app.web.infrastructure.startup.main_app import main
            await main()
            return True
        except ImportError as ie:
            logger.error(f"Failed to import web application main module: {ie}")
            return False
        except Exception as e:
            logger.error(f"Error running web application main: {e}")
            return False
            
    except Exception as e:
        error_details = str(e)
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        logger.error(f"Critical error starting web application: {error_details}")
        logger.error(f"Exception type: {error_type}")
        logger.error(f"Stack trace: \n{stack_trace}")
        return False

if __name__ == "__main__":
    success = asyncio.run(start_web())
    sys.exit(0 if success else 1)
