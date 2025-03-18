"""Bot container entrypoint."""
import os
import sys
import asyncio
import logging
import traceback

from app.shared.infrastructure.startup.bootstrap import ApplicationBootstrap

logger = logging.getLogger("homelab.bot")

def start_bot():
    """Start the Discord bot."""
    try:
        # Set container type
        os.environ["CONTAINER_TYPE"] = "bot"
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the application
        bootstrap = ApplicationBootstrap("bot")
        if not loop.run_until_complete(bootstrap.initialize()):
            logger.error("Bot initialization failed")
            sys.exit(1)
        
        # Start the bot
        from app.bot.core.main import main
        loop.run_until_complete(main())
        
    except Exception as e:
        logger.error(f"Bot startup failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

# Add this block to make the module executable
if __name__ == "__main__":
    start_bot()