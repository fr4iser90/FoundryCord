from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.core.extensions import session_extension
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity
from typing import Optional
from sqlalchemy import select

logger = get_web_logger()
router = APIRouter(prefix="/v1/servers", tags=["Server Selection"])

class ServerSelectorController:
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("/select")(self.select_guild)
        self.router.get("/current")(self.get_current_guild)
    
    async def select_guild(self, request: Request, guild_id: Optional[str] = None, current_user=Depends(get_current_user)):
        """Select a guild and store it in session"""
        try:
            session = session_extension(request)
            
            if guild_id:
                # Verify guild exists and user has access
                async with session_context() as db_session:
                    result = await db_session.execute(
                        select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                    )
                    guild = result.scalar_one_or_none()
                    
                    if not guild:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Guild not found"
                        )
                
                # Store in session
                session['selected_guild'] = guild_id
                return {"message": f"Selected guild {guild_id}", "guild_id": guild_id}
            else:
                # Clear selection
                session['selected_guild'] = None
                return {"message": "Guild selection cleared"}
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error selecting guild: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_current_guild(self, request: Request, current_user=Depends(get_current_user)):
        """Get currently selected guild from session"""
        try:
            session = session_extension(request)
            guild_id = session.get('selected_guild')
            
            if not guild_id:
                return {"guild_id": None}
            
            # Get guild details
            async with session_context() as db_session:
                result = await db_session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    session['selected_guild'] = None
                    return {"guild_id": None}
                
                return {
                    "guild_id": guild.guild_id,
                    "name": guild.name,
                    "is_verified": guild.is_verified
                }
                
        except Exception as e:
            logger.error(f"Error getting current guild: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance
server_selector_controller = ServerSelectorController()
select_guild = server_selector_controller.select_guild
get_current_guild = server_selector_controller.get_current_guild 