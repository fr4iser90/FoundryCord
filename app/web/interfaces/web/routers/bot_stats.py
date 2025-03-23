from fastapi import APIRouter, Depends
from sqlalchemy import func
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import Guild
from app.web.infrastructure.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/bot-stats")

@router.get("/overview")
async def get_overview_stats(current_user = Depends(get_current_user)):
    async with session_context() as session:
        # Hole Statistiken aus der Datenbank
        guilds_query = await session.execute(
            select(
                func.count(Guild.id).label('total_guilds'),
                func.sum(Guild.member_count).label('total_members'),
                func.count(Guild.id).filter(Guild.is_active == True).label('active_guilds')
            )
        )
        stats = guilds_query.first()
        
        return {
            "status": "ONLINE",  # TODO: Implementiere echte Status-Prüfung
            "server_count": stats.total_guilds,
            "active_servers": stats.active_guilds,
            "total_users": stats.total_members,
            "online_users": 0,  # TODO: Implementiere Online-User-Tracking
            "command_count": 0,  # TODO: Implementiere Command-Tracking
            "recent_commands": 0
        }