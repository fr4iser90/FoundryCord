# app/shared/infrastructure/docker/entrypoint.py

import os
import sys
import logging
import asyncio
from app.shared.infrastructure.config.env_manager import EnvManager
from app.shared.infrastructure.security.security_bootstrapper import SecurityBootstrapper
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

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
    
    # Initialize database connection first
    logger.info("Establishing database connection...")
    try:
        from app.shared.infrastructure.config.env_manager import configure_database
        engine, Session = configure_database()
        logger.info("Database connection established successfully")
        
        # Store the session factory for global use
        from app.shared.infrastructure.database.session import set_session_factory
        set_session_factory(Session)
        
        # Initialize database if needed
        logger.info("Starting database initialization...")
        from app.shared.infrastructure.database.migrations.init_db import init_db
        if not await init_db(engine=engine, session=Session):
            logger.error("Database initialization failed")
            return None
            
        # Now initialize security bootstrapper with database support
        logger.info("Initializing security key storage...")
        security = SecurityBootstrapper(auto_db_key_management=True)
        await security.initialize()
        
        logger.info("Web interface initialization complete")
        return config
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def bootstrap_web():
    """Entrypoint for the web container"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        config = loop.run_until_complete(_bootstrap_web_async())
        
        if config is None:
            logger.error("Web initialization failed")
            sys.exit(1)
            
        logger.info("Web initialization successful")
        return config
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