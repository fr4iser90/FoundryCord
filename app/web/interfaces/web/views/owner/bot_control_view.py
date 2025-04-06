from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.web.core.extensions import templates_extension, session_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from app.web.interfaces.api.rest.v1.owner.owner_controller import (
    list_servers,
    add_server,
    remove_server
)

router = APIRouter(prefix="/owner/bot", tags=["Bot Control"])
templates = templates_extension()
logger = get_web_logger()

class BotControlView:
    """View for bot control functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        # HTML Routes
        self.router.get("", response_class=HTMLResponse)(self.bot_control_page)
        
        # API Routes
        self.router.post("/start")(self.start_bot)
        self.router.post("/stop")(self.stop_bot)
        self.router.post("/restart")(self.restart_bot)
        self.router.post("/servers/add")(self.add_server)
        self.router.delete("/servers/{guild_id}")(self.remove_server)
        self.router.get("/servers")(self.list_servers)
        self.router.get("/config")(self.get_config)
        self.router.post("/servers/{guild_id}/join")(self.join_server)
        self.router.post("/servers/{guild_id}/leave")(self.leave_server)
        self.router.post("/servers/{guild_id}/access")(self.update_server_access)
    
    async def bot_control_page(self, request: Request, current_user=Depends(get_current_user)):
        """Render bot control page"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get session and active guild
            session = session_extension(request)
            active_guild = session.get('active_guild')
            
            # Get bot configuration and server list
            bot_connector = await get_bot_connector()
            config = await bot_connector.get_bot_config(current_user)
            
            # Initialize empty server list
            servers = []
            
            # Get bot instance to access workflows
            bot = await bot_connector.get_bot()
            if bot:
                # Get guild workflow to access guild data
                guild_workflow = bot.workflow_manager.get_workflow("guild")
                if guild_workflow:
                    # Get all servers with their current status
                    for guild in await guild_workflow.get_all_guilds():
                        # Ensure access_status has a default value
                        access_status = guild.access_status if hasattr(guild, 'access_status') else 'PENDING'
                        
                        server_data = {
                            "guild_id": guild.guild_id,
                            "name": guild.name,
                            "is_active": await guild_workflow.is_guild_active(guild.guild_id),
                            "access_status": access_status,
                            "member_count": guild.member_count,
                            "joined_at": guild.joined_at,
                            "access_requested_at": guild.access_requested_at if hasattr(guild, 'access_requested_at') else None,
                            "access_reviewed_at": guild.access_reviewed_at if hasattr(guild, 'access_reviewed_at') else None,
                            "icon_url": guild.icon_url if hasattr(guild, 'icon_url') else None
                        }
                        servers.append(server_data)
                        logger.debug(f"Added server to list: {server_data}")
                else:
                    logger.warning("Guild workflow not found in bot instance")
            else:
                logger.warning("Bot instance not available - showing empty server list")
            
            # Log the number of pending servers
            pending_count = len([s for s in servers if s['access_status'] == 'PENDING'])
            logger.info(f"Found {pending_count} pending servers out of {len(servers)} total servers")
            
            return templates.TemplateResponse(
                "views/owner/bot.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "bot-control",
                    "config": config,
                    "servers": servers,
                    "active_guild": active_guild,
                    "bot_status": "offline" if not bot else "online"
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to bot control: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": current_user, "error": str(e.detail)},
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in bot control view: {e}")
            return templates.TemplateResponse(
                "views/errors/500.html",
                {
                    "request": request, 
                    "user": current_user, 
                    "error": "Failed to load bot control page. The bot might be offline or not properly initialized."
                },
                status_code=500
            )
    
    async def start_bot(self, request: Request, current_user=Depends(get_current_user)):
        """Start the bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            result = await bot_connector.start_bot(current_user)
            return JSONResponse({"status": "success", "message": "Bot started successfully"})
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def stop_bot(self, request: Request, current_user=Depends(get_current_user)):
        """Stop the bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            result = await bot_connector.stop_bot(current_user)
            return JSONResponse({"status": "success", "message": "Bot stopped successfully"})
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def restart_bot(self, request: Request, current_user=Depends(get_current_user)):
        """Restart the bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            result = await bot_connector.restart_bot(current_user)
            return JSONResponse({"status": "success", "message": "Bot restarted successfully"})
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def add_server(self, request: Request, current_user=Depends(get_current_user)):
        """Add a new server"""
        try:
            await require_role(current_user, Role.OWNER)
            data = await request.json()
            result = await add_server(current_user, data)
            return JSONResponse({"status": "success", "message": "Server added successfully"})
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def remove_server(self, request: Request, guild_id: str, current_user=Depends(get_current_user)):
        """Remove a server"""
        try:
            await require_role(current_user, Role.OWNER)
            result = await remove_server(current_user, guild_id)
            return JSONResponse({"status": "success", "message": "Server removed successfully"})
        except Exception as e:
            logger.error(f"Error removing server: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def list_servers(self, request: Request, current_user=Depends(get_current_user)):
        """List all servers"""
        try:
            await require_role(current_user, Role.OWNER)
            servers = await list_servers(current_user)
            return JSONResponse({"status": "success", "servers": servers})
        except Exception as e:
            logger.error(f"Error listing servers: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
    
    async def get_config(self, request: Request, current_user=Depends(get_current_user)):
        """Get bot configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            config = await bot_connector.get_bot_config(current_user)
            return JSONResponse({"status": "success", "config": config})
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
            
    async def join_server(self, request: Request, guild_id: str, current_user=Depends(get_current_user)):
        """Make bot join a server"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            result = await bot_connector.join_server(guild_id, current_user)
            return JSONResponse({"status": "success", "message": f"Bot joined server {guild_id} successfully"})
        except Exception as e:
            logger.error(f"Error joining server: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )
            
    async def leave_server(self, request: Request, guild_id: str, current_user=Depends(get_current_user)):
        """Make bot leave a server"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            result = await bot_connector.leave_server(guild_id, current_user)
            return JSONResponse({"status": "success", "message": f"Bot left server {guild_id} successfully"})
        except Exception as e:
            logger.error(f"Error leaving server: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )

    async def update_server_access(self, request: Request, guild_id: str, current_user=Depends(get_current_user)):
        """Update server access status"""
        try:
            await require_role(current_user, Role.OWNER)
            data = await request.json()
            
            bot_connector = await get_bot_connector()
            bot = await bot_connector.get_bot()
            
            if not bot:
                return JSONResponse(
                    {"status": "error", "detail": "Bot instance not found"},
                    status_code=404
                )
            
            guild_workflow = bot.workflow_manager.get_workflow("guild")
            if not guild_workflow:
                return JSONResponse(
                    {"status": "error", "detail": "Guild workflow not found"},
                    status_code=404
                )
            
            status = data.get("status")
            if status == "APPROVED":
                success = await guild_workflow.approve_guild(guild_id)
            elif status == "DENIED":
                success = await guild_workflow.deny_guild(guild_id)
            elif status == "BLOCKED":
                success = await guild_workflow.deny_guild(guild_id)  # Same as deny for now
            else:
                return JSONResponse(
                    {"status": "error", "detail": "Invalid access status"},
                    status_code=400
                )
            
            if not success:
                return JSONResponse(
                    {"status": "error", "detail": "Failed to update guild access status"},
                    status_code=500
                )
            
            return JSONResponse({
                "status": "success",
                "message": f"Server {guild_id} access status updated to {status}"
            })
            
        except Exception as e:
            logger.error(f"Error updating server access: {e}")
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )

# Create view instance
bot_control_view = BotControlView()
