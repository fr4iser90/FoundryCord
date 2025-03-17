"""Database initialization and table creation."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.models.base import Base

logger = get_db_logger()

async def create_tables(engine: AsyncEngine) -> bool:
    """Create all database tables defined in the models"""
    try:
        logger.info("Checking for existing database tables...")
        
        # First, check if tables already exist
        async with engine.connect() as conn:
            # Check if the categories table exists (as a representative table)
            result = await conn.execute(text("SELECT to_regclass('public.categories')"))
            table_exists = result.scalar() is not None
            
            if table_exists:
                logger.info("Database tables already exist, skipping creation")
                return True
        
        # If we get here, tables don't exist, so create them
        logger.info("Creating database tables...")
        
        # Import all models to make sure they're registered with the metadata
        # These imports need to be here to make sure all models are loaded
        from app.bot.infrastructure.database.models import CategoryEntity, ChannelEntity, CategoryPermissionEntity, ChannelPermissionEntity
        
        # Create tables with explicit engine connection and transaction
        async with engine.begin() as conn:
            # Create all tables defined in Base
            await conn.run_sync(Base.metadata.create_all)
            
            # Execute explicit SQL to verify table creation
            await conn.execute(text("""
            DO $$
            BEGIN
                -- Create category tables if they don't exist
                IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'categories') THEN
                    CREATE TABLE categories (
                        id SERIAL PRIMARY KEY,
                        discord_id BIGINT UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        position INTEGER NOT NULL DEFAULT 0,
                        permission_level VARCHAR(50) NOT NULL,
                        is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                        is_created BOOLEAN NOT NULL DEFAULT FALSE,
                        metadata_json JSONB
                    );
                END IF;
                
                IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'category_permissions') THEN
                    CREATE TABLE category_permissions (
                        id SERIAL PRIMARY KEY,
                        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                        role_id BIGINT NOT NULL,
                        view BOOLEAN NOT NULL DEFAULT FALSE,
                        send_messages BOOLEAN NOT NULL DEFAULT FALSE,
                        manage_messages BOOLEAN NOT NULL DEFAULT FALSE,
                        manage_channels BOOLEAN NOT NULL DEFAULT FALSE,
                        manage_category BOOLEAN NOT NULL DEFAULT FALSE
                    );
                END IF;
                
                -- Create channel tables if they don't exist
                IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'channels') THEN
                    CREATE TABLE channels (
                        id SERIAL PRIMARY KEY,
                        discord_id BIGINT UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        category_id INTEGER REFERENCES categories(id),
                        category_discord_id BIGINT,
                        type VARCHAR(50) NOT NULL,
                        position INTEGER NOT NULL DEFAULT 0,
                        permission_level VARCHAR(50) NOT NULL,
                        is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                        is_created BOOLEAN NOT NULL DEFAULT FALSE,
                        nsfw BOOLEAN NOT NULL DEFAULT FALSE,
                        slowmode_delay INTEGER NOT NULL DEFAULT 0,
                        topic TEXT,
                        thread_config JSONB,
                        metadata_json JSONB
                    );
                END IF;
                
                IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'channel_permissions') THEN
                    CREATE TABLE channel_permissions (
                        id SERIAL PRIMARY KEY,
                        channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
                        role_id BIGINT NOT NULL,
                        view BOOLEAN NOT NULL DEFAULT FALSE,
                        send_messages BOOLEAN NOT NULL DEFAULT FALSE,
                        read_messages BOOLEAN NOT NULL DEFAULT FALSE,
                        manage_messages BOOLEAN NOT NULL DEFAULT FALSE,
                        manage_channel BOOLEAN NOT NULL DEFAULT FALSE,
                        use_bots BOOLEAN NOT NULL DEFAULT FALSE,
                        embed_links BOOLEAN NOT NULL DEFAULT FALSE,
                        attach_files BOOLEAN NOT NULL DEFAULT FALSE,
                        add_reactions BOOLEAN NOT NULL DEFAULT FALSE
                    );
                END IF;
            END $$;
            """))
        
        # Verify tables exist
        async with engine.connect() as conn:
            # Test categories table
            try:
                result = await conn.execute(text("SELECT 1 FROM categories LIMIT 1"))
                logger.info("Categories table exists and is accessible")
            except Exception as e:
                logger.error(f"Categories table verification failed: {e}")
                return False
                
            # Test channels table
            try:
                result = await conn.execute(text("SELECT 1 FROM channels LIMIT 1"))
                logger.info("Channels table exists and is accessible")
            except Exception as e:
                logger.error(f"Channels table verification failed: {e}")
                return False
        
        logger.info("All database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in database table operation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False 