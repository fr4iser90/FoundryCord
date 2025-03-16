from sqlalchemy.ext.asyncio import AsyncEngine
from app.shared.infrastructure.database.models import Base
from app.shared.infrastructure.database.models.config import initialize_engine, initialize_session
import asyncio
from app.shared.interface.logging.api import get_db_logger

from sqlalchemy import select, inspect, text

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
        
        # First check if we can connect
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        
        # Then create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        await initialize_session()
        logger.info("Database tables created successfully")
        
        # Run migrations for existing users
        await migrate_existing_users()
        
        # Run dashboard components migration
        await migrate_dashboard_components()
        
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def migrate_existing_users():
    """Migrate existing users from env to database"""
    # Import innerhalb der Funktion, um zirkuläre Importe zu vermeiden
    from app.shared.infrastructure.database.constants.user_constants import (
        SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
    )
    from app.shared.infrastructure.database.models import User
    from app.shared.infrastructure.database.models.config import get_async_session

    # Neue Session für diesen spezifischen Prozess erstellen
    async_session = await get_async_session()
    
    try:
        for role_group, role_name in [
            (SUPER_ADMINS, 'super_admin'),
            (ADMINS, 'admin'),
            (MODERATORS, 'moderator'),
            (USERS, 'user'),
            (GUESTS, 'guest')
        ]:
            for username, discord_id in role_group.items():
                # Prüfen ob Benutzer bereits existiert
                existing_user = await async_session.execute(
                    select(User).where(User.discord_id == discord_id)
                )
                existing_user = existing_user.scalar_one_or_none()
                
                if existing_user is None:
                    # Nur hinzufügen wenn der Benutzer noch nicht existiert
                    user = User(
                        discord_id=discord_id,
                        username=username,
                        role=role_name
                    )
                    async_session.add(user)
                    logger.info(f"Added new user: {username} with role {role_name}")
                else:
                    logger.debug(f"User {username} already exists, skipping")
        
        await async_session.commit()
        logger.info("User migration completed successfully")
    finally:
        # Session am Ende ordnungsgemäß schließen
        await async_session.close()

async def migrate_dashboard_components():
    """Migrate dashboard components from code to database"""
    try:
        # Import and run the existing dashboard components migration
        from app.shared.infrastructure.database.migrations.dashboards import dashboard_components_migration
        logger.info("Starting dashboard components migration...")
        await dashboard_components_migration.main()
        logger.info("Dashboard component migration completed successfully")
    except Exception as e:
        logger.error(f"Dashboard components migration failed: {e}")
        raise

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