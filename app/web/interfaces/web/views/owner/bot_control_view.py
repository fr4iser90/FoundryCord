from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.web.core.extensions import templates_extension, session_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.integration.bot_connector import get_bot_connector

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
        
        # API Routes - Only HTML view related endpoints should be here
        self.router.get("/config")(self.get_config)
    
    async def bot_control_page(self, request: Request, current_user=Depends(get_current_user)):
        """Render bot control page"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get bot configuration and status
            bot_connector = await get_bot_connector()
            bot = await bot_connector.get_bot()
            
            # Default values when bot is offline
            bot_status = "offline"
            bot_stats = None
            config = {
                "command_prefix": "!",
                "auto_reconnect": True,
                "log_level": "INFO",
                "status_update_interval": 60,
                "max_reconnect_attempts": 5
            }
            
            if bot:
                bot_status = "online" if bot.is_ready() else "connecting"
                config = await bot_connector.get_bot_config(current_user)
                
                # Get bot statistics if online
                if bot_status == "online":
                    bot_stats = {
                        "uptime": bot.uptime if hasattr(bot, "uptime") else 0,
                        "active_servers_count": len(bot.guilds) if hasattr(bot, "guilds") else 0,
                        "total_members": sum(g.member_count for g in bot.guilds) if hasattr(bot, "guilds") else 0,
                        "commands_today": 0  # TODO: Implement command tracking
                    }
            
            # Prepare template context
            context = {
                "request": request,
                "user": current_user,
                "active_page": "bot-control",
                "config": config,
                "bot_status": bot_status,
                "bot_latency": round(bot.latency * 1000, 2) if bot and hasattr(bot, "latency") else None,
                "bot_stats": bot_stats
            }
            
            # Render the main template which includes our component templates
            return templates.TemplateResponse(
                "views/owner/bot/bot.html",
                context
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
            # Return a more graceful error page that still shows the UI
            context = {
                "request": request,
                "user": current_user,
                "active_page": "bot-control",
                "config": {},
                "bot_status": "offline",
                "bot_latency": None,
                "bot_stats": None,
                "error": "Bot is currently offline or not properly initialized. Some features may be unavailable."
            }
            return templates.TemplateResponse(
                "views/owner/bot/bot.html",
                context
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

# Create view instance
bot_control_view = BotControlView()
