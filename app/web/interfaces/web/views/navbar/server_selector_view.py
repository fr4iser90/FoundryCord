from fastapi import APIRouter, Request, Depends, HTTPException
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/servers", tags=["Server Selection"])
templates = Jinja2Templates(directory="app/web/templates")
logger = get_web_logger()

class ServerSelectorView:
    """View for server selection - renders HTML templates and provides API endpoints"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register routes for this view"""
        self.router.get("/select")(self.server_selector_page)
        self.router.get("/list")(self.get_approved_servers)  # New endpoint for approved servers
        self.router.post("/select/{guild_id}")(self.select_server)
    
    async def server_selector_page(self, request: Request):
        """Render the server selector page"""
        return templates.TemplateResponse(
            "navbar/server_selector.html",
            {"request": request}
        )

    async def get_approved_servers(self, current_user=Depends(get_current_user)):
        """Get list of approved servers only"""
        try:
            logger.info(f"Getting approved servers for user: {current_user}")
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.access_status.ilike('approved'))
                )
                servers = result.scalars().all()
                
                logger.info(f"Found {len(servers)} approved servers")
                server_list = []
                
                for server in servers:
                    logger.debug(f"Processing server: {server.name} (ID: {server.guild_id})")
                    server_list.append({
                        "guild_id": server.guild_id,
                        "name": server.name,
                        "icon_url": server.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                        "member_count": server.member_count,
                        "access_status": server.access_status
                    })
                
                return server_list
                
        except Exception as e:
            logger.error(f"Error getting approved servers: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def select_server(self, guild_id: str, request: Request, current_user=Depends(get_current_user)):
        """Select a server for the current session"""
        try:
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(
                        GuildEntity.guild_id == guild_id,
                        GuildEntity.access_status.ilike('approved')
                    )
                )
                server = result.scalar_one_or_none()
                
                if not server:
                    raise HTTPException(status_code=404, detail="Server not found or not approved")
                
                # Store in session
                request.session['selected_guild'] = {
                    "guild_id": server.guild_id,
                    "name": server.name,
                    "icon_url": server.icon_url
                }
                
                return {"message": "Server selected successfully"}
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error selecting server: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# View instance
server_selector_view = ServerSelectorView()
