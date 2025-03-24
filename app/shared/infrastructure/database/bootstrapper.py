"""
Database bootstrapper for initializing the database.

This module is the centralized entry point for all database initialization
operations, including:
1. Waiting for the PostgreSQL server to be available
2. Creating the database schema if it doesn't exist
3. Running migrations to update the schema
4. Seeding initial data if needed

Usage:
    await initialize_database()
"""
import asyncio
import logging
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres
from app.shared.infrastructure.database.migrations.init_db import init_db, is_database_empty
from app.shared.infrastructure.database.migrations.migration_service import MigrationService
from app.shared.infrastructure.database.core.credentials import DatabaseCredentialManager

logger = get_db_logger()

async def initialize_database() -> bool:
    """
    Initialize the database by:
    1. Waiting for PostgreSQL to be available
    2. Creating initial schema if needed
    3. Running migrations
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Step 1: Wait for PostgreSQL to be available 
        if not await wait_for_postgres():
            logger.error("Failed to connect to PostgreSQL after multiple attempts")
            return False
        
        # Initialize basic database structure is handled by postgres ???
        # Step 2: Initialize basic database structure
        #if not await init_db():
        #    logger.error("Failed to initialize database schema")
        #    return False
            
        # Step 3: Run migrations to update schema to latest version
        migration_service = MigrationService()
        if not await migration_service.check_migrations():
            logger.error("Failed to run database migrations")
            return False
        
        logger.debug("Database initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def execute_migrations() -> bool:
    """Run database migrations independently."""
    try:
        migration_service = MigrationService()
        return await migration_service.run_migrations()
    except Exception as e:
        logger.error(f"Failed to execute migrations: {e}")
        return False

async def check_database_status() -> dict:
    """
    Check the status of the database.
    
    Returns:
        dict: Information about the database status
    """
    try:
        # Check PostgreSQL connection
        if not await wait_for_postgres(max_attempts=1, silent=True):
            return {
                "status": "unavailable",
                "message": "Cannot connect to PostgreSQL server"
            }
            
        # Get database credentials
        credential_manager = DatabaseCredentialManager()
        creds = credential_manager.get_credentials()
        
        # Create engine for checking status
        db_url = f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
        engine = create_async_engine(db_url)
        
        # Check if database is empty
        is_empty = await is_database_empty(engine)
        
        # Check migration status
        migration_service = MigrationService()
        migration_current = await migration_service.check_migrations()
        
        return {
            "status": "available",
            "database": creds['database'],
            "host": creds['host'],
            "is_empty": is_empty,
            "migrations_checked": migration_current
        }
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    asyncio.run(initialize_database()) 