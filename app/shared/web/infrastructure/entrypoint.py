"""Web container entrypoint."""
import os
import sys
import asyncio
import logging
import traceback

from app.shared.infrastructure.startup.bootstrap import ApplicationBootstrap

logger = logging.getLogger("homelab.bot")

def start_web():
    """Start the web interface."""
    try:
        # Set container type
        os.environ["CONTAINER_TYPE"] = "web"
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the application
        bootstrap = ApplicationBootstrap("web")
        if not loop.run_until_complete(bootstrap.initialize()):
            logger.error("Web initialization failed")
            sys.exit(1)
        
        # Start the web server
        from app.web.core.main import start_web_server
        start_web_server(bootstrap.dependency_container)
        
    except Exception as e:
        logger.error(f"Web startup failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

# Add this block to make the module executable
if __name__ == "__main__":
    start_web()