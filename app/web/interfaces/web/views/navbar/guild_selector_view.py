from fastapi import APIRouter, Request, Depends, HTTPException
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/guilds", tags=["Guild Selection"])
templates = Jinja2Templates(directory="app/web/templates")
logger = get_web_logger()

class GuildSelectorView:
    """View for guild selection - renders HTML templates and provides API endpoints"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register routes for this view"""
        self.router.get("/select")(self.guild_selector_page)
        self.router.get("/list")(self.get_approved_guilds)
        self.router.post("/select/{guild_id}")(self.select_guild)
    
    async def guild_selector_page(self, request: Request):
        """Render the guild selector page"""
        return templates.TemplateResponse(
            "navbar/guild_selector.html",
            {"request": request}
        )

    async def get_approved_guilds(self, current_user=Depends(get_current_user)):
        """Get list of approved guilds only"""
        try:
            logger.info(f"Getting approved guilds for user: {current_user}")
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.access_status.ilike('approved'))
                )
                guilds = result.scalars().all()
                
                logger.info(f"Found {len(guilds)} approved guilds")
                guild_list = []
                
                for guild in guilds:
                    logger.debug(f"Processing guild: {guild.name} (ID: {guild.guild_id})")
                    guild_list.append({
                        "guild_id": guild.guild_id,
                        "name": guild.name,
                        "icon_url": guild.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png",
                        "member_count": guild.member_count,
                        "access_status": guild.access_status
                    })
                
                return guild_list
                
        except Exception as e:
            logger.error(f"Error getting approved guilds: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def select_guild(self, guild_id: str, request: Request, current_user=Depends(get_current_user)):
        """Select a guild for the current session"""
        try:
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(
                        GuildEntity.guild_id == guild_id,
                        GuildEntity.access_status.ilike('approved')
                    )
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found or not approved")
                
                # Store in session
                request.session['selected_guild'] = {
                    "guild_id": guild.guild_id,
                    "name": guild.name,
                    "icon_url": guild.icon_url
                }
                
                return {"message": "Guild selected successfully"}
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error selecting guild: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# View instance
guild_selector_view = GuildSelectorView()
