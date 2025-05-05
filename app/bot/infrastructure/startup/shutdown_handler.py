import asyncio
import logging
import signal
import sys
from typing import Optional
import nextcord.ext.commands as commands
from app.shared.interfaces.logging.api import get_bot_logger

logger = logging.getLogger("homelab.bot")

class ShutdownHandler:
    """Handler for graceful bot shutdown on system signals"""
    
    def __init__(self, bot):
        self.bot = bot
        self.shutdown_event = asyncio.Event()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        
        # Allow for graceful shutdown
        bot.loop.set_exception_handler(self._handle_loop_exception)
        
        logger.debug("Shutdown handler initialized")
    
    def _handle_sigint(self, sig, frame):
        """Handle SIGINT (Ctrl+C)"""
        logger.info("Received SIGINT, initiating graceful shutdown...")
        self._initiate_shutdown()
    
    def _handle_sigterm(self, sig, frame):
        """Handle SIGTERM"""
        logger.info("Received SIGTERM, initiating graceful shutdown...")
        self._initiate_shutdown()
    
    def _handle_loop_exception(self, loop, context):
        """Handle unhandled exceptions in the event loop"""
        exception = context.get("exception")
        if exception:
            logger.error(f"Unhandled exception in event loop: {exception}")
            logger.error(f"Context: {context}")
            
            # If this is a critical error, initiate shutdown
            if isinstance(exception, (SystemExit, KeyboardInterrupt)):
                self._initiate_shutdown()
    
    def _initiate_shutdown(self):
        """Initiate the shutdown sequence"""
        logger.info("Initiating bot shutdown...")
        
        # Create a task to handle the shutdown
        asyncio.create_task(self._shutdown())
        
        # Set the shutdown event
        self.shutdown_event.set()
    
    async def _shutdown(self):
        """Perform the shutdown sequence"""
        try:
            # First, clean up all workflows via the workflow manager
            await self.bot.cleanup()
            
            # Then close the bot
            if not self.bot.is_closed():
                await self.bot.close()
                
            logger.info("Bot shutdown completed")
            
            # Exit after a short delay
            await asyncio.sleep(1)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            # Force exit if shutdown failed
            sys.exit(1)