"""Application bootstrap module."""
import asyncio
import logging
from typing import Optional

from app.shared.infrastructure.database.bootstrapper import initialize_database
from app.shared.infrastructure.security.security_bootstrapper import initialize_security
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

async def bootstrap_application() -> bool:
    """
    Bootstrap the complete application with all required services.
    This is the central initialization point for all components.
    
    Returns:
        bool: True if bootstrap was successful, False otherwise
    """
    try:
        logger.info("Starting application bootstrap...")
        
        # 1. Initialize database first (most critical component)
        logger.info("Initializing database...")
        if not await initialize_database():
            logger.error("Database initialization failed")
            return False
        
        # 2. Initialize security services
        logger.info("Initializing security services...")
        if not await initialize_security():
            logger.error("Security initialization failed")
            return False

        # More initialization steps can be added here as needed
        
        logger.info("Application bootstrap completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Application bootstrap failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False