# app/shared/infrastructure/docker/entrypoint.py

import os
import sys
import logging
import asyncio
from app.shared.infrastructure.config.env_manager import EnvManager
from app.shared.infrastructure.security.security_bootstrapper import SecurityBootstrapper

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("homelab.entrypoint")

async def _bootstrap_bot_async():
    """Async implementation of bootstrap_bot"""
    logger.info("===== Homelab Discord Bot Initialization =====")
    
    # Initialize security bootstrapper for environment variables
    security = SecurityBootstrapper(auto_db_key_management=False)
    security._ensure_env_keys()  # Just ensure env vars are set
    
    # Then load environment variables
    env_manager = EnvManager()
    config = env_manager.configure()
    
    # Initialize database
    logger.info("Starting database initialization...")
    from app.shared.infrastructure.database.migrations.init_db import init_db
    if not await init_db():
        logger.error("Database initialization failed")
        return None
        
    # Now initialize full security bootstrapper with database support
    logger.info("Initializing security key storage...")
    security = SecurityBootstrapper(auto_db_key_management=True)
    await security.initialize()
        
    # Now import and get the bot set up
    logger.info("Starting the Discord bot...")
    from app.bot.core.main import setup_bot
    bot = setup_bot()
    
    # Return the bot - we'll start it outside the async context
    return bot, config

def bootstrap_bot():
    """Entrypoint for the bot container"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot, config = loop.run_until_complete(_bootstrap_bot_async())
        
        # Now run the bot with its own event loop management
        logger.info("Running the bot...")
        bot.run(bot.env_config.DISCORD_BOT_TOKEN)
        
        return config
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

async def _bootstrap_web_async():
    """Async implementation of bootstrap_web"""
    logger.info("===== Homelab Discord Bot Web Interface Initialization =====")
    
    # Initialize security bootstrapper for environment variables
    security = SecurityBootstrapper(auto_db_key_management=False)
    security._ensure_env_keys()  # Just ensure env vars are set
    
    # Then load environment variables
    env_manager = EnvManager()
    config = env_manager.configure()
    
    # Initialize database and key storage
    logger.info("Initializing security key storage...")
    security = SecurityBootstrapper(auto_db_key_management=True)
    await security.initialize()
    
    logger.info("Web interface initialization complete")
    return config

def bootstrap_web():
    """Entrypoint for the web container"""
    try:
        return asyncio.run(_bootstrap_web_async())
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "bot":
            bootstrap_bot()
        elif sys.argv[1] == "web":
            bootstrap_web()
        else:
            logger.error(f"Unknown service type: {sys.argv[1]}")
            sys.exit(1)
    else:
        logger.error("No service type specified (bot or web)")
        sys.exit(1)