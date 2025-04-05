from fastapi import APIRouter, Depends, HTTPException
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/api/servers", tags=["Server Selector"])
logger = get_web_logger()

class ServerSelectorView:
    """View für Server-Auswahl"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/list")(self.get_available_servers)
        self.router.post("/switch/{guild_id}")(self.switch_server)
    
    async def get_available_servers(self, current_user=Depends(get_current_user)):
        """Get list of available servers for the current user"""
        try:
            # Debug-Ausgabe des aktuellen Benutzers
            logger.debug(f"Current user: {current_user}")
            
            async with session_context() as session:
                # Vereinfachte Abfrage ohne Filter
                result = await session.execute(
                    select(GuildEntity)
                )
                servers = result.scalars().all()
                
                # Debug-Ausgabe der gefundenen Server
                logger.debug(f"Found {len(servers)} servers")
                for server in servers:
                    logger.debug(f"Server: {server.name} (ID: {server.guild_id})")
                
                return [{
                    "id": server.guild_id,
                    "name": server.name,
                    "icon_url": server.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                    "member_count": getattr(server, 'member_count', 0)
                } for server in servers]
        except Exception as e:
            logger.error(f"Error getting available servers: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def switch_server(self, guild_id: str, current_user=Depends(get_current_user)):
        """Switch the current active server"""
        try:
            async with session_context() as session:
                # Vereinfachte Abfrage ohne owner_id-Filter
                result = await session.execute(
                    select(GuildEntity).where(
                        GuildEntity.guild_id == guild_id
                    )
                )
                server = result.scalars().first()
                
                if not server:
                    raise HTTPException(status_code=404, detail="Server not found")
                
                return {
                    "success": True,
                    "server": {
                        "id": server.guild_id,
                        "name": server.name,
                        "icon_url": server.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png"
                    }
                }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error switching server: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# View-Instanz erzeugen
server_selector_view = ServerSelectorView()
get_available_servers = server_selector_view.get_available_servers
switch_server = server_selector_view.switch_server
