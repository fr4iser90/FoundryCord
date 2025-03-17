# app/shared/infrastructure/docker/entrypoint.py

import os
import sys
import logging
import asyncio
from pathlib import Path
from app.shared.infrastructure.config.env_manager import EnvManager
from app.shared.infrastructure.security.security_bootstrapper import SecurityBootstrapper
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

async def setup_security():
    """Set up security components asynchronously"""
    security = SecurityBootstrapper(auto_db_key_management=True)
    await security.initialize()
    return security

async def run_dashboard_migrations():
    """Run dashboard migrations to populate the database"""
    try:
        # Check if we're running in the bot container to avoid duplicate migrations
        container_type = os.environ.get("CONTAINER_TYPE", "unknown")
        logger.info(f"Current container type: {container_type}")
        
        if container_type != "bot":
            logger.info(f"Skipping dashboard migrations in {container_type} container")
            return True
            
        logger.info("Starting dashboard components migration...")
        # Use main instead of run_migrations since that's the actual function name
        from app.shared.infrastructure.database.migrations.dashboards.dashboard_components_migration import main
        await main()
        logger.info("Dashboard components migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Dashboard migration failed: {e}")
        return False

async def main():
    """Main entrypoint for the bot"""
    try:
        # Set container type environment variable BEFORE any calls
        os.environ["CONTAINER_TYPE"] = "bot"
        logger.info("Running in BOT container mode")
        
        # Initialize security
        security = await setup_security()
        logger.info("Security bootstrapping completed")
        
        # Run dashboard migrations (only in bot container)
        await run_dashboard_migrations()
        
        # Import and start the bot
        logger.info("Starting bot...")
        from app.bot.core.main import main as bot_main
        await bot_main()
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

async def _bootstrap_web_async():
    """Async implementation of bootstrap_web"""
    logger.info("===== Homelab Discord Bot Web Interface Initialization =====")
    
    # Set container type environment variable BEFORE any calls
    os.environ["CONTAINER_TYPE"] = "web"
    logger.info("Running in WEB container mode")
    
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
        
        # We explicitly skip dashboard migrations in web container now
        logger.info("Web container will not run dashboard migrations")
            
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
            asyncio.run(main())
        elif sys.argv[1] == "web":
            bootstrap_web()
        else:
            logger.error(f"Unknown service type: {sys.argv[1]}")
            sys.exit(1)
    else:
        logger.error("No service type specified (bot or web)")
        sys.exit(1)