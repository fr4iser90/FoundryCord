"""Migration script to create the Config table."""
import asyncio
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os

from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.core.credentials import DatabaseCredentialManager

logger = get_db_logger()

# Define the Config model for direct table creation
Base = declarative_base()

class Config(Base):
    """Config model for storing key-value pairs."""
    __tablename__ = 'config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

async def create_config_table():
    """Create the Config table if it doesn't exist."""
    # Get database credentials from credential manager
    credential_manager = DatabaseCredentialManager()
    creds = credential_manager.get_credentials()
    
    # Construct the database URL
    db_url = f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
    
    # Create async engine
    engine = create_async_engine(db_url)
    
    try:
        # Check if table exists
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT to_regclass('config')"))
            table_exists = await result.scalar()
            
            if not table_exists:
                logger.info("Creating config table...")
                # Create the table
                await conn.run_sync(Base.metadata.create_all, tables=[Config.__table__])
                logger.info("Config table created successfully")
            else:
                logger.info("Config table already exists")
                
        return True
    except Exception as e:
        logger.error(f"Failed to create config table: {e}")
        return False
    finally:
        await engine.dispose()

# Run the migration if executed directly
if __name__ == "__main__":
    asyncio.run(create_config_table())
