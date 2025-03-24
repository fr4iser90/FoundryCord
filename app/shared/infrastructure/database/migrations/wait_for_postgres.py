#!/usr/bin/env python3
"""PostgreSQL connection checker module."""
import asyncio
import os
import sys
import time
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

async def wait_for_postgres():
    """Wait for PostgreSQL to be ready. Requires environment variables to be set."""
    # Erforderliche Umgebungsvariablen ohne Fallbacks
    required_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'APP_DB_USER', 'APP_DB_PASSWORD', 'POSTGRES_DB']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Database connection cannot be established without proper configuration")
        return False
        
    # Alle Variablen sind vorhanden, können sicher verwendet werden
    db_host = os.environ['POSTGRES_HOST']
    db_port = os.environ['POSTGRES_PORT'] 
    db_user = os.environ['APP_DB_USER']
    db_pass = os.environ['APP_DB_PASSWORD']
    db_name = os.environ['POSTGRES_DB']
    
    logger.debug(f"Attempting to connect to PostgreSQL at {db_host}:{db_port}")
    
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_async_engine(db_url)
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with engine.connect() as conn:
                # Execute a simple query to check if the database is ready
                # Use text() to create a SQL expression
                await conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            retry_count += 1
            logger.info(f"Waiting for PostgreSQL... ({retry_count}/{max_retries})")
            if retry_count >= max_retries:
                logger.error(f"Could not connect to PostgreSQL: {e}")
                return False
            await asyncio.sleep(2)
    
    return False

if __name__ == "__main__":
    if not asyncio.run(wait_for_postgres()):
        sys.exit(1)