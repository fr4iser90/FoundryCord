from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.core.extensions import session_extension
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from typing import Optional, List, Dict
from sqlalchemy import select

logger = get_web_logger()
router = APIRouter(prefix="/v1/servers", tags=["Server Selection"])

class ServerSelectorController:
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for server selection"""
        self.router.get("")(self.get_servers)  # List all servers
        self.router.get("/current")(self.get_current_server)  # Get current selection
        self.router.post("/select")(self.select_server)  # Select a server
    
    async def get_servers(self, current_user=Depends(get_current_user)) -> List[Dict]:
        """Get list of available servers for the current user"""
        try:
            logger.debug(f"Current user: {current_user}")
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity)
                )
                servers = result.scalars().all()
                
                logger.debug(f"Found {len(servers)} servers")
                server_list = []
                
                for server in servers:
                    logger.debug(f"Server: {server.name} (ID: {server.guild_id})")
                    server_list.append({
                        "id": server.guild_id,
                        "name": server.name,
                        "icon_url": server.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                        "member_count": server.member_count,
                        "status": server.access_status,
                        "is_verified": server.is_verified
                    })
                
                return server_list
                
        except Exception as e:
            logger.error(f"Error getting available servers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_current_server(self, request: Request, current_user=Depends(get_current_user)):
        """Get currently selected server from session"""
        try:
            session = session_extension(request)
            guild_id = session.get('selected_guild')
            
            if not guild_id:
                return {"guild_id": None}
            
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
                    "icon_url": guild.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                    "status": guild.access_status,
                    "is_verified": guild.is_verified
                }
                
        except Exception as e:
            logger.error(f"Error getting current server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def select_server(self, request: Request, guild_id: str, current_user=Depends(get_current_user)):
        """Select a server and store it in session"""
        try:
            session = session_extension(request)
            
            async with session_context() as db_session:
                result = await db_session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Server not found"
                    )
                
                if guild.access_status != "APPROVED":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Server is not approved for access"
                    )
                
                # Store in session
                session['selected_guild'] = guild_id
                return {
                    "message": f"Selected server {guild_id}",
                    "guild_id": guild_id,
                    "name": guild.name,
                    "icon_url": guild.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                    "status": guild.access_status,
                    "is_verified": guild.is_verified
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error selecting server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance
server_selector_controller = ServerSelectorController()
get_servers = server_selector_controller.get_servers
get_current_server = server_selector_controller.get_current_server
select_server = server_selector_controller.select_server 