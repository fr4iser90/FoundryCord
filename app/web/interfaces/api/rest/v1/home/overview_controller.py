from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities import GuildEntity
from sqlalchemy import select, func

logger = get_web_logger()
router = APIRouter(prefix="/home", tags=["Home Overview"])

class HomeOverviewController:
    """Controller for home overview functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        self.router.get("/stats")(self.get_overview_stats)
    
    async def get_overview_stats(self, current_user=Depends(get_current_user)):
        """Get overview statistics for the home dashboard"""
        try:
            async with session_context() as session:
                # Get statistics from database
                guilds_query = await session.execute(
                    select(
                        func.count(GuildEntity.id).label('total_guilds'),
                        func.sum(GuildEntity.member_count).label('total_members'),
                        func.count(GuildEntity.id).filter(GuildEntity.is_verified == True).label('active_guilds')
                    )
                )
                
                guild_stats = guilds_query.one()
                
                stats = {
                    "total_guilds": guild_stats.total_guilds or 0,
                    "total_members": guild_stats.total_members or 0,
                    "active_guilds": guild_stats.active_guilds or 0,
                    "command_count": 0,  # TODO: Implement command tracking
                    "recent_commands": 0  # TODO: Implement command tracking
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance and export functions
home_overview_controller = HomeOverviewController()
get_overview_stats = home_overview_controller.get_overview_stats 