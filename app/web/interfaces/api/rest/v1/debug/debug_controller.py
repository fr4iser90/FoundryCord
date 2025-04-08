from fastapi import APIRouter, Depends, HTTPException
from app.web.application.services.auth.dependencies import get_current_user
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from sqlalchemy import select, inspect
from app.shared.interface.logging.api import get_web_logger

router = router = APIRouter(prefix="/debug", tags=["Debug"])
logger = get_web_logger()

@router.get("/guilds")
async def debug_guilds(current_user=Depends(get_current_user)):
    """Debug endpoint to display all guilds in the database"""
    try:
        async with session_context() as session:
            result = await session.execute(select(GuildEntity))
            guilds = result.scalars().all()
            
            return [{
                "id": guild.guild_id,
                "name": guild.name,
                "icon_url": guild.icon_url,
                "member_count": getattr(guild, 'member_count', 0)
            } for guild in guilds]
    except Exception as e:
        logger.error(f"Error in debug_guilds: {e}")
        return {"error": str(e)}

@router.post("/add-test-guild")
async def add_test_guild(current_user=Depends(get_current_user)):
    """Adds a test guild to the database"""
    try:
        async with session_context() as session:
            # Check if already exists
            result = await session.execute(
                select(GuildEntity).where(GuildEntity.guild_id == "151414244603068426")
            )
            existing = result.scalars().first()
            
            if existing:
                return {"message": "Test guild already exists", "guild": {
                    "id": existing.guild_id,
                    "name": existing.name
                }}
            
            # Create new guild
            guild = GuildEntity(
                guild_id="151414244603068426",
                name="LeL",
                icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
                member_count=21
            )
            session.add(guild)
            await session.commit()
            
            return {"message": "Test guild added successfully", "guild": {
                "id": guild.guild_id,
                "name": guild.name
            }}
    except Exception as e:
        logger.error(f"Error adding test guild: {e}")
        return {"error": str(e)}

@router.get("/db-status")
async def debug_db_status(current_user=Depends(get_current_user)):
    """Debug endpoint to display database status"""
    try:
        async with session_context() as session:
            # Check if connection works
            result = await session.execute("SELECT 1")
            connection_ok = result.scalar() == 1
            
            # List tables
            tables_result = await session.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            tables = [row[0] for row in tables_result]
            
            # Count entries in important tables
            counts = {}
            for table in ['discord_guilds', 'app_users', 'discord_guild_users']:
                if table in tables:
                    count_result = await session.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = count_result.scalar()
                else:
                    counts[table] = "Table not found"
            
            return {
                "connection": "OK" if connection_ok else "Failed",
                "tables": tables,
                "record_counts": counts
            }
    except Exception as e:
        logger.error(f"Error in debug_db_status: {e}")
        return {"error": str(e)}

@router.post("/add-test-guild-with-details")
async def add_test_guild_with_details(
    guild_id: str,
    name: str,
    icon_url: str = "https://cdn.discordapp.com/embed/avatars/0.png",
    member_count: int = 21,
    current_user=Depends(get_current_user)
):
    """Adds a custom test guild to the database"""
    try:
        async with session_context() as session:
            # Check if already exists
            result = await session.execute(
                select(GuildEntity).where(GuildEntity.guild_id == guild_id)
            )
            existing = result.scalars().first()
            
            if existing:
                return {"message": "Test guild already exists", "guild": {
                    "id": existing.guild_id,
                    "name": existing.name
                }}
            
            # Create new guild
            guild = GuildEntity(
                guild_id=guild_id,
                name=name,
                icon_url=icon_url,
                member_count=member_count
            )
            session.add(guild)
            await session.commit()
            
            return {"message": "Test guild added successfully", "guild": {
                "id": guild.guild_id,
                "name": guild.name
            }}
    except Exception as e:
        logger.error(f"Error adding test guild: {e}")
        return {"error": str(e)}

@router.get("/check-schema")
async def check_schema(current_user=Depends(get_current_user)):
    """Checks if the database schema is correct"""
    try:
        async with session_context() as session:
            inspector = inspect(session.bind)
            
            # Check if important tables exist
            tables = inspector.get_table_names()
            required_tables = ['discord_guilds', 'app_users', 'discord_guild_users']
            missing_tables = [table for table in required_tables if table not in tables]
            
            # Check columns in guild table
            guild_columns = []
            if 'discord_guilds' in tables:
                guild_columns = [col['name'] for col in inspector.get_columns('discord_guilds')]
            
            return {
                "tables_exist": len(missing_tables) == 0,
                "missing_tables": missing_tables,
                "guild_columns": guild_columns
            }
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return {"error": str(e)}
