from sqlalchemy.ext.asyncio import AsyncEngine
from app.shared.infrastructure.database.models import Base
from app.shared.infrastructure.database.core.config import initialize_engine, initialize_session
import asyncio
from app.shared.interface.logging.api import get_db_logger

from sqlalchemy import select, inspect, text

# Import our new database migration wait function
from app.shared.infrastructure.database.migrations.dashboards.dashboard_components_migration import wait_for_initialization

logger = get_db_logger()

async def is_database_empty():
    """Check if database has no tables (is empty)"""
    engine = await initialize_engine()
    async with engine.begin() as conn:
        # Get the inspector to check for existing tables
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        # Get list of tables
        tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        
        # If there are no tables, the database is empty
        is_empty = len(tables) == 0
        logger.info(f"Database check: {'Empty database' if is_empty else 'Database already has tables'}")
        return is_empty

async def init_db(bot=None):
    try:
        engine = await initialize_engine()
        
        # Create a schema in PostgreSQL
        async with engine.begin() as conn:
            # Create tables using SQLAlchemy models
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database schema created successfully")
        
        # If database was empty, run initial data migrations
        if await is_database_empty():
            logger.info("Running initial data migrations for empty database")
            await migrate_existing_users()
        
        # Now wait for dashboard migrations to complete (whether they're running in another process or not)
        await wait_for_initialization()
        
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def migrate_existing_users():
    """
    Migrate existing users from environment variables to database.
    This is for initial setup only.
    """
    import os
    from app.shared.infrastructure.database.models.user import User
    
    # Create an async session for user migration
    async_session = await initialize_session()
    
    try:
        # Get super admin user IDs from environment
        super_admins_env = os.environ.get('SUPER_ADMINS', '')
        
        if not super_admins_env:
            logger.warning("No SUPER_ADMINS defined in environment variables")
            return
        
        # Parse super admins from environment (format: "NAME|ID,NAME2|ID2")
        super_admins = []
        for admin_entry in super_admins_env.split(','):
            if '|' in admin_entry:
                name, discord_id = admin_entry.split('|', 1)
                super_admins.append((name.strip(), discord_id.strip()))
        
        if not super_admins:
            logger.warning("No valid super admin entries found in SUPER_ADMINS environment variable")
            return
        
        # Migrate each super admin
        for name, discord_id in super_admins:
            # Check if user already exists
            existing_user = await async_session.execute(
                select(User).where(User.discord_id == discord_id)
            )
            existing_user = existing_user.scalars().first()
            
            if existing_user:
                logger.info(f"Super admin {name} (ID: {discord_id}) already exists in database")
                # Update roles if needed
                if 'super_admin' not in existing_user.roles:
                    existing_user.roles.append('super_admin')
                    logger.info(f"Updated roles for {name} (ID: {discord_id})")
            else:
                # Create new user
                new_user = User(
                    discord_id=discord_id,
                    username=name,
                    roles=['super_admin'],
                    is_active=True
                )
                async_session.add(new_user)
                logger.info(f"Created super admin user: {name} (ID: {discord_id})")
        
        await async_session.commit()
        logger.info("User migration completed successfully")
    finally:
        # Session am Ende ordnungsgemäß schließen
        await async_session.close()

# Let the dashboard_components_migration.py handle itself separately
# No need to call it from here as it has its own initialization system now

# Wrapper für den Migrations-Code um einen eigenen Event-Loop zu verwenden
def run_migration():
    """Run the migration in a separate event loop"""
    # Verwende einen komplett isolierten Prozess für die Migration
    try:
        asyncio.run(migrate_existing_users())
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        
if __name__ == "__main__":
    run_migration()