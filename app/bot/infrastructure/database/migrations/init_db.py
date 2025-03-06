from sqlalchemy.ext.asyncio import AsyncEngine
from ..models.models import Base
from ..models.config import initialize_engine, initialize_session
import asyncio
from core.services.logging.logging_commands import logger
from sqlalchemy import select

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
    from domain.auth.models import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
    from ..models.models import User
    from ..models.config import async_session
    
    async with async_session() as session:
        for role_group, role_name in [
            (SUPER_ADMINS, 'super_admin'),
            (ADMINS, 'admin'),
            (MODERATORS, 'moderator'),
            (USERS, 'user'),
            (GUESTS, 'guest')
        ]:
            for username, discord_id in role_group.items():
                # Prüfen ob Benutzer bereits existiert
                existing_user = await session.execute(
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
                    session.add(user)
                    logger.info(f"Added new user: {username} with role {role_name}")
                else:
                    logger.debug(f"User {username} already exists, skipping")
        
        await session.commit()
        logger.info("User migration completed successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(migrate_existing_users())