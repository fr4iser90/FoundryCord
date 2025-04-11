from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.domain.auth.policies import is_authorized
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from typing import Dict
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.interfaces.api.rest.v1.base_controller import BaseController

logger = get_web_logger()
router = APIRouter(prefix="/owner/bot", tags=["Bot Control"])

class BotControlController(BaseController):
    """Controller for bot control functionality"""
    
    def __init__(self):
        super().__init__(prefix="/owner/bot", tags=["Bot Control"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Bot Control Functions
        self.router.post("/start")(self.start_bot)
        self.router.post("/stop")(self.stop_bot)
        self.router.post("/restart")(self.restart_bot)
        self.router.get("/status")(self.get_bot_status)
        
        # Bot Configuration
        self.router.get("/config")(self.get_bot_config)
        self.router.put("/config")(self.update_bot_config)
    
    async def start_bot(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Start the Discord bot"""
        try:
            if not await self.authz_service.check_permission(current_user, "MANAGE_BOT"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            bot_connector = await get_bot_connector()
            await bot_connector.start_bot(current_user)
            return self.success_response("Bot started successfully")
        except Exception as e:
            return self.handle_exception(e)
    
    async def stop_bot(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Stop the Discord bot"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can stop bot"
                )
            bot_connector = await get_bot_connector()
            await bot_connector.stop_bot(current_user)
            return self.success_response("Bot stopped successfully")
        except Exception as e:
            return self.handle_exception(e)
    
    async def restart_bot(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Restart the Discord bot"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can restart bot"
                )
            bot_connector = await get_bot_connector()
            await bot_connector.restart_bot(current_user)
            return self.success_response("Bot restarted successfully")
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_bot_status(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get current bot status"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view bot status"
                )
            bot_connector = await get_bot_connector()
            status_data = await bot_connector.get_status()
            
            if not status_data:
                return self.success_response({
                    "status": "offline",
                    "uptime": 0,
                    "latency": 0,
                    "guilds": 0,
                    "total_members": 0,
                    "commands_today": 0
                })
            
            # Add total members and commands today if not present
            if "total_members" not in status_data:
                status_data["total_members"] = sum(g.member_count for g in status_data.get("guilds", []))
            if "commands_today" not in status_data:
                status_data["commands_today"] = 0
                
            return self.success_response(status_data)
            
        except Exception as e:
            return self.handle_exception(e)

    async def get_bot_config(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get current bot configuration"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view bot config"
                )
            bot_connector = await get_bot_connector()
            config = await bot_connector.get_bot_config(current_user)
            return self.success_response(config)
        except Exception as e:
            return self.handle_exception(e)
    
    async def update_bot_config(self, config: dict, current_user: AppUserEntity = Depends(get_current_user)):
        """Update bot configuration"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can update bot config"
                )
            bot_connector = await get_bot_connector()
            await bot_connector.get_bot_config(current_user)
            return self.success_response("Bot configuration updated successfully")
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
bot_control_controller = BotControlController()
start_bot = bot_control_controller.start_bot
stop_bot = bot_control_controller.stop_bot
restart_bot = bot_control_controller.restart_bot
get_bot_config = bot_control_controller.get_bot_config
update_bot_config = bot_control_controller.update_bot_config
get_bot_status = bot_control_controller.get_bot_status 