"""Database migration service."""
import asyncio
import logging
import os
import subprocess
import traceback
from pathlib import Path
from app.shared.interfaces.logging.api import get_db_logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logger = get_db_logger()

class MigrationService:
    """Service for managing database migrations."""
    
    def __init__(self):
        """Initialize the Migration Service."""
        self.alembic_dir = Path("/app/shared/infrastructure/database/migrations/alembic")
        self.alembic_ini = self.alembic_dir / "alembic.ini"

    async def verify_database_connection(self) -> bool:
        """Verify database connection before running migrations."""
        try:
            from app.shared.infrastructure.database.core.credentials import DatabaseCredentialManager
            creds = DatabaseCredentialManager().get_credentials()
            db_url = f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
            engine = create_async_engine(db_url)
            
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database connection verified successfully")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    async def run_migrations(self) -> bool:
        """Execute all pending migrations."""
        try:
            if not await self.verify_database_connection():
                logger.error("Cannot proceed with migrations - database connection failed")
                return False

            if not self.alembic_ini.exists():
                logger.error(f"alembic.ini not found at: {self.alembic_ini}")
                return False
            
            logger.info("Executing database migrations...")
            os.chdir(str(self.alembic_dir))
            
            # Debug output for migration files
            try:
                all_files = os.listdir(str(self.alembic_dir))
                versions_dir = self.alembic_dir / 'versions'
                version_files = os.listdir(str(versions_dir)) if versions_dir.exists() else []
                
                logger.info(f"Files in alembic directory: {all_files}")
                logger.info(f"Migration files: {version_files}")
                
                logger.debug(f"Alembic files check:")
                logger.debug(f"  alembic.ini exists: {self.alembic_ini.exists()}")
                logger.debug(f"  alembic/env.py exists: {(self.alembic_dir / 'env.py').exists()}")
                logger.debug(f"  alembic/versions/ exists: {(self.alembic_dir / 'versions').exists()}")
            except Exception as e:
                logger.error(f"Could not list migration files: {e}")
            
            # Execute migrations
            result = subprocess.run(
                ["alembic", "upgrade", "head"], 
                capture_output=True,
                text=True,
                cwd=str(self.alembic_dir)
            )
            
            # Only log as error if it contains actual error messages
            if result.stderr and not result.stderr.startswith('INFO'):
                logger.error(f"Migration errors: {result.stderr}")
            else:
                logger.debug(f"Migration output: {result.stderr}")

            
            if result.returncode != 0:
                logger.error(f"Migrations failed with code: {result.returncode}")
                return False
            
            logger.info("Migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration execution failed: {e}")
            logger.error(traceback.format_exc())
            return False

    async def check_migrations(self) -> bool:
        """Check if migrations are needed and run them if necessary."""
        try:
            # Erst prüfen, ob Migrationen ausgeführt werden müssen
            os.chdir(str(self.alembic_dir))
            check_result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=str(self.alembic_dir)
            )
            
            logger.debug(f"Migration status: {check_result.stdout.strip()}")
            
            # Wenn keine Migration aktiv ist oder nicht die neueste, führe Migrationen aus
            if "head" not in check_result.stdout:
                logger.info("Migrations need to be run")
                if not await self.run_migrations():
                    logger.error("Failed to run migrations")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking migrations: {e}")
            return False
