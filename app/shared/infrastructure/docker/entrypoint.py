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
    try:
        # First ensure database is ready
        from app.shared.infrastructure.database.core.init import wait_for_database
        
        # Wait for database with retry logic
        max_retries = 5
        retry_delay = 2
        db_ready = False
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Database readiness check (attempt {attempt}/{max_retries})...")
            if await wait_for_database():
                logger.info("Database is ready for security bootstrapping")
                db_ready = True
                break
                
            if attempt < max_retries:
                logger.info(f"Waiting {retry_delay}s before retrying...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        # Initialize security with database if available
        security = SecurityBootstrapper(auto_db_key_management=db_ready)
        await security.initialize()
        
        return security
    except Exception as e:
        logger.error(f"Security setup failed: {e}", exc_info=True)
        # Fall back to environment-only security
        security = SecurityBootstrapper(auto_db_key_management=False)
        security._ensure_env_keys()
        return security

async def run_dashboard_migrations():
    """Run dashboard migrations to populate the database"""
    try:
        # Check if we're running in the bot container
        container_type = os.environ.get("CONTAINER_TYPE", "unknown")
        logger.info(f"Dashboard migration in {container_type} container")
        
        # Only the bot container should run dashboard migrations
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

async def run_database_migrations():
    """Run database migrations to ensure tables exist"""
    try:
        # Check container type
        container_type = os.environ.get("CONTAINER_TYPE", "unknown")
        logger.info(f"Database migration in {container_type} container")
        
        # Only the web container should create database tables
        if container_type != "web":
            logger.info(f"Checking if database is ready ({container_type} container)...")
            # Bot container should wait for database to be ready but not create tables
            from app.shared.infrastructure.database.core.init import wait_for_database
            max_retries = 5
            retry_delay = 2
            
            for attempt in range(1, max_retries + 1):
                logger.info(f"Database readiness check (attempt {attempt}/{max_retries})...")
                if await wait_for_database():
                    logger.info("Database is ready")
                    return True
                if attempt < max_retries:
                    logger.info(f"Waiting {retry_delay}s before retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
            
            logger.error("Database not ready after maximum retries")
            return False
        
        # From here, only WEB container code runs
        logger.info("Starting database migrations (web container)...")
        from app.shared.infrastructure.database.models.base import initialize_engine, initialize_tables
        
        # Initialize database engine
        engine = await initialize_engine()
        logger.info("Database engine created successfully")
        
        # Create database tables with retry logic
        max_retries = 3
        retry_delay = 2
        for attempt in range(1, max_retries + 1):
            try:
                await initialize_tables()
                logger.info("Database tables created successfully")
                break
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Database table creation failed (attempt {attempt}): {e}")
                    logger.info(f"Waiting {retry_delay}s before retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Database table creation failed after {max_retries} attempts: {e}")
                    return False
        
        # Run init_db only after tables are created
        from app.shared.infrastructure.database.migrations.init_db import init_db
        await init_db()
        
        return True
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        
        # Check if database is ready - do NOT create tables from bot container
        logger.info("Checking database readiness...")
        db_ready = await run_database_migrations()
        if not db_ready:
            logger.warning("Database not ready, but continuing with bot startup")
        
        # Start the bot without waiting for dashboard migrations to complete
        logger.info("Starting bot...")
        # Run dashboard migrations in the background 
        asyncio.create_task(run_dashboard_migrations())
        
        from app.bot.core.main import main as bot_main
        await bot_main()
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

async def _bootstrap_web_async():
    """Async implementation of bootstrap_web"""
    try:
        # Wait for database with retry logic
        from app.shared.infrastructure.database.core.init import wait_for_database
        
        # Wait for database with retry logic
        max_retries = 5
        retry_delay = 2
        db_ready = False
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Database readiness check (attempt {attempt}/{max_retries})...")
            if await wait_for_database():
                logger.info("Database is ready for web initialization")
                db_ready = True
                break
                
            if attempt < max_retries:
                logger.info(f"Waiting {retry_delay}s before retrying...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        if not db_ready:
            logger.error("Database not available after maximum retries")
            return None
        
        # Initialize database connection
        logger.info("Initializing database connection")
        from app.shared.infrastructure.database.core.connection import get_db_connection
        db_conn = await get_db_connection()
        logger.info("Database connection initialized successfully")
        
        # Then load environment variables
        env_manager = EnvManager()
        config = env_manager.configure()
        
        # Now initialize security bootstrapper with database support
        logger.info("Initializing security key storage...")
        security = SecurityBootstrapper(auto_db_key_management=True)
        await security.initialize()
        
        logger.info("Web interface initialization complete")
        return config
    except Exception as e:
        logger.error(f"Web initialization failed: {e}")
        return None

def bootstrap_web():
    """Entrypoint for the web container"""
    try:
        logger.info("===== Homelab Discord Bot Web Interface Initialization =====")
        
        # Set container type environment variable BEFORE any calls
        os.environ["CONTAINER_TYPE"] = "web"
        logger.info("Running in WEB container mode")
        
        # Initialize security bootstrapper for environment variables
        # Just ensure env vars are set temporarily for startup
        security = SecurityBootstrapper(auto_db_key_management=False)
        security._ensure_env_keys()
        
        # Create an event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async initialization
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