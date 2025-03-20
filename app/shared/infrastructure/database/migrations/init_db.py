"""Database initialization module."""
import asyncio
import logging
import os
import subprocess
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import time

from app.shared.infrastructure.database.core.credentials import DatabaseCredentialManager
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

async def is_database_empty(engine) -> bool:
    """Check if the database is empty (no tables exist)."""
    try:
        async with engine.connect() as conn:
            # Check if any tables exist in the public schema
            result = await conn.execute(text(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            table_count = await result.scalar()
            
            if table_count == 0:
                logger.warning("Database is empty (no tables)")
                return True
                
            logger.info(f"Database has {table_count} tables")
            return False
    except Exception as e:
        logger.error(f"Failed to check if database is empty: {e}")
        # Assume not empty on error to be safe
        return False

async def init_db():
    """Initialize the database with proper schema and initial data."""
    try:
        logger.info("Starting database initialization...")
        
        # First ensure PostgreSQL is available
        logger.info("Ensuring database is available before initialization...")
        if not await wait_for_postgres():  # Use default parameters
            logger.error("Database not available after waiting")
            return False
            
        logger.info("Database is available, proceeding with schema creation")
        
        # Get credentials from the credential manager 
        credential_manager = DatabaseCredentialManager()
        creds = credential_manager.get_credentials()
        
        # Create the connection URL
        db_url = f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
        
        # Create engine
        engine = create_async_engine(db_url)
        
        # KORREKTE LÖSUNG: Direkt prüfen, ob die Tabellen existieren, ohne den bool zu awaiten
        has_tables = False
        try:
            async with engine.connect() as conn:
                # Check for security_keys table
                result = await conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'security_keys')"
                ))
                has_security_keys = await result.scalar()
                
                if has_security_keys:
                    logger.info("Security keys table exists")
                    has_tables = True
                else:
                    logger.info("Security keys table doesn't exist")
        except Exception as e:
            logger.debug(f"Error checking critical tables: {e}")
            # Fallback: Tabellen erstellen
        
        if not has_tables:
            logger.info("Critical tables missing. Creating essential tables...")
            
            # Create security tables (NOT handled by Alembic)
            if not await create_security_tables(engine):
                logger.error("Failed to create security tables")
                return False
                
            logger.info("Critical tables created successfully")
        else:
            logger.info("Critical tables already exist - skipping direct creation")
            
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        stack_trace = traceback.format_exc()
        logger.error(f"Stack trace: \n{stack_trace}")
        return False

# Diese Funktion wird jetzt direkter in init_db() integriert und nicht mehr aufgerufen
async def check_critical_tables(engine) -> bool:
    """Check if critical tables exist."""
    try:
        async with engine.connect() as conn:
            # Check for security_keys table
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'security_keys')"
            ))
            has_security_keys = await result.scalar()
            
            if not has_security_keys:
                logger.warning("Security keys table doesn't exist")
                return False
                
            logger.info("All critical tables exist")
            return True
    except Exception as e:
        # Catch exceptions explicitly, log them, and return a value
        logger.error(f"Failed to check critical tables: {e}")
        return False

async def create_security_tables(engine) -> bool:
    """Create security related tables that aren't part of Alembic migrations."""
    try:
        async with engine.begin() as conn:
            # Create security_keys table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS security_keys (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            logger.info("Security tables created successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to create security tables: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(init_db())