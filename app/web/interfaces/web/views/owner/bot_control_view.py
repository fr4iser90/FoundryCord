from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.interface.logging.api import get_web_logger
# REMOVED: Old BotConnector import
# from app.shared.infrastructure.integration.OLD import get_bot_connector
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class BotControlView(BaseView):
    """View for bot control functionality"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/owner/bot", tags=["Bot Control"]))
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        self.router.get("", response_class=HTMLResponse)(self.bot_control_page)
        self.router.get("/config")(self.get_config)
    
    async def bot_control_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render bot control page - Uses Depends for current_user"""
        try:
            # Permission check now uses the user injected by Depends
            await self.require_permission(current_user, "OWNER")
            
            # TODO: Fetch bot status and config from the API endpoints in BotControlController
            #       instead of using the old BotConnector here. 
            #       The template will need JavaScript to fetch this data dynamically.

            # REMOVED: Old BotConnector usage
            # bot_connector = await get_bot_connector()
            # bot = await bot_connector.get_bot()
            
            # Default/Placeholder values - these should be fetched via API
            bot_status = "unknown" # Placeholder
            bot_stats = None       # Placeholder
            config = {             # Placeholder
                "command_prefix": "?",
                "auto_reconnect": False,
                "log_level": "UNKNOWN",
                "status_update_interval": 0,
                "max_reconnect_attempts": 0
            }
            bot_latency = None     # Placeholder

            # REMOVED: Logic depending on old 'bot' object and connector
            # if bot:
            #     bot_status = "online" if bot.is_ready() else "connecting"
            #     # TODO: Fetch config from API instead
            #     # config = await bot_connector.get_bot_config(current_user)
            #     
            #     # Get bot statistics if online
            #     if bot_status == "online":
            #         # TODO: Fetch stats from API instead
            #         bot_stats = {
            #             "uptime": bot.uptime if hasattr(bot, "uptime") else 0,
            #             "active_servers_count": len(bot.guilds) if hasattr(bot, "guilds") else 0,
            #             "total_members": sum(g.member_count for g in bot.guilds) if hasattr(bot, "guilds") else 0,
            #             "commands_today": 0  # TODO: Implement command tracking via API
            #         }
            # 
            # bot_latency = round(bot.latency * 1000, 2) if bot and hasattr(bot, "latency") else None
            
            return self.render_template(
                "owner/control/index.html",
                request,
                active_page="owner-control",
                config=config, # Pass placeholder config
                bot_status=bot_status, # Pass placeholder status
                bot_latency=bot_latency, # Pass placeholder latency
                bot_stats=bot_stats # Pass placeholder stats
            )
        except HTTPException as http_exc:
            # Re-raise HTTPExceptions directly to be handled globally
            raise http_exc 
        except Exception as e:
            # Log other exceptions and return a generic 500 error page
            self.logger.error(f"Error rendering bot control page: {e}", exc_info=True)
            return self.error_response(request, "An unexpected error occurred while loading the bot control page.", 500)
    
    async def get_config(self, request: Request):
        """Get bot configuration - TODO: This endpoint might be redundant if page fetches from controller API"""
        try:
            # TODO: This should likely call the BotControlController API endpoint instead of using BotConnector.
            #       Or, this endpoint might be removed if the main page fetches data dynamically.
            # current_user = await self.get_current_user(request)
            # await self.require_permission(current_user, "MANAGE_BOT")
            # bot_connector = await get_bot_connector()
            # config = await bot_connector.get_bot_config(current_user)
            # return JSONResponse({"status": "success", "config": config})
            self.logger.warning("get_config view endpoint is currently disabled.")
            return JSONResponse(
                {"status": "error", "detail": "Not Implemented Yet"},
                status_code=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            self.logger.error(f"Error in get_config view: {e}", exc_info=True)
            return JSONResponse(
                {"status": "error", "detail": str(e)},
                status_code=500
            )

# View instance
bot_control_view = BotControlView()
router = bot_control_view.router
