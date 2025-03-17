# @/app/bot/core/main.py
import os
import nextcord
import sys
import asyncio
import signal
from dotenv import load_dotenv
from nextcord.ext import commands
from app.shared.interface.logging.api import get_bot_logger, setup_bot_logging
from app.bot.infrastructure.factories import BotComponentFactory, ServiceFactory, TaskFactory, DashboardFactory
from app.shared.infrastructure.config.env_config import EnvConfig  # Import the shared EnvConfig
from app.bot.core.bot import HomelabBot
from app.bot.core.lifecycle.lifecycle_manager import LifecycleManager
from app.bot.infrastructure.factories.composite.bot_factory import BotComponentFactory


# Get a reference to the logger
logger = get_bot_logger()

# Load environment configuration
env_config = EnvConfig()
env_config.load()

# Initialize environment variables
load_dotenv()

# Initialize bot with environment settings
bot = HomelabBot(
    command_prefix='!!' if env_config.is_development else '!',
    intents=env_config.get_intents()
)

# Attach env_config to bot
bot.env_config = env_config

async def initialize_bot():
    """Initialize the bot and its components."""
    global bot
    
    try:
        # Initialize component factory - pass the bot instance
        factory = BotComponentFactory(bot)
        bot.factory = factory
        
        # Initialize lifecycle manager
        lifecycle = LifecycleManager(bot)
        bot.lifecycle = lifecycle
        
        # Initialize bot components
        await lifecycle.initialize()
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        
async def shutdown_bot():
    """Shutdown the bot gracefully."""
    global bot
    
    if bot:
        try:
            # Use lifecycle manager to shutdown
            if bot.lifecycle:
                await bot.lifecycle.shutdown()
                
            # Close the bot
            await bot.close()
            
            logger.info("Bot shutdown successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    # Exit the program
    sys.exit(0)

def signal_handler():
    """Handle termination signals."""
    logger.info("Received termination signal")
    asyncio.create_task(shutdown_bot())

@bot.event
async def on_ready():
    try:
        # Just keep this - the service workflow will handle logging setup
        await initialize_bot()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

# Add these two functions for entrypoint.py to use
def setup_bot():
    """Return the bot object for use by entrypoint.py"""
    return bot

async def run_bot_async(bot_instance):
    """Async version that entrypoint.py can use"""
    # This is just a placeholder for now - entrypoint will run the bot
    return bot_instance

# Original function - untouched
def run_bot():
    try:
        bot.run(env_config.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)

async def main():
    """Main entry point for the bot."""
    global bot
    
    try:
        # Create bot instance
        bot = HomelabBot(command_prefix='!')
        
        # Set up signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
            
        # Get token
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("No Discord bot token found in environment variables")
            return
            
        # Run the bot
        logger.info("Running the bot...")
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        
        # Exit with error
        sys.exit(1)

# Run the bot if this module is executed directly
if __name__ == "__main__":
    asyncio.run(main())
