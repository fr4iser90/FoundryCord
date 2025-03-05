from sqlalchemy.ext.asyncio import AsyncEngine
from core.database.models import Base
from core.database.config import initialize_engine, initialize_session
import asyncio
from core.services.logging.logging_commands import logger

async def init_db(bot=None):
    engine = await initialize_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize session after engine is created
    await initialize_session()
    
    logger.info("Database tables created successfully")
    return True

async def migrate_existing_users():
    """Migrate existing users from env to database"""
    from core.services.auth.models.users import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
    from core.database.models import User
    from core.database.config import async_session
    
    async with async_session() as session:
        # Migrate super admins
        for username, discord_id in SUPER_ADMINS.items():
            user = User(
                discord_id=discord_id,
                username=username,
                role='super_admin'
            )
            session.add(user)
        
        # Migrate admins
        for username, discord_id in ADMINS.items():
            user = User(
                discord_id=discord_id,
                username=username,
                role='admin'
            )
            session.add(user)
        
        # Continue for other roles...
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(migrate_existing_users())