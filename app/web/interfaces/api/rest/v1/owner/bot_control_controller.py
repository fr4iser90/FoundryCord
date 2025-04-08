from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from typing import Dict

logger = get_web_logger()
router = APIRouter(prefix="/owner/bot", tags=["Bot Control"])

class BotControlController:
    """Controller for bot control functionality"""
    
    def __init__(self):
        self.router = router
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
    
    async def start_bot(self, current_user=Depends(get_current_user)):
        """Start the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.start()
            return {"message": "Bot started successfully"}
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def stop_bot(self, current_user=Depends(get_current_user)):
        """Stop the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.stop()
            return {"message": "Bot stopped successfully"}
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def restart_bot(self, current_user=Depends(get_current_user)):
        """Restart the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.restart()
            return {"message": "Bot restarted successfully"}
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_bot_status(self, current_user=Depends(get_current_user)):
        """Get current bot status"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            bot = await bot_connector.get_bot()
            
            if not bot:
                return {
                    "status": "offline",
                    "uptime": 0,
                    "latency": 0,
                    "guilds": 0
                }
            
            return {
                "status": "online" if bot.is_ready() else "connecting",
                "uptime": bot.uptime if hasattr(bot, "uptime") else 0,
                "latency": round(bot.latency * 1000, 2) if hasattr(bot, "latency") else 0,
                "guilds": len(bot.guilds) if hasattr(bot, "guilds") else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_bot_config(self, current_user=Depends(get_current_user)):
        """Get current bot configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            config = await bot_connector.get_config()
            return config
        except Exception as e:
            logger.error(f"Error getting bot config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_bot_config(self, config: Dict, current_user=Depends(get_current_user)):
        """Update bot configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.update_config(config)
            return {"message": "Bot configuration updated successfully"}
        except Exception as e:
            logger.error(f"Error updating bot config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance
bot_control_controller = BotControlController()
start_bot = bot_control_controller.start_bot
stop_bot = bot_control_controller.stop_bot
restart_bot = bot_control_controller.restart_bot
get_bot_config = bot_control_controller.get_bot_config
update_bot_config = bot_control_controller.update_bot_config
get_bot_status = bot_control_controller.get_bot_status 