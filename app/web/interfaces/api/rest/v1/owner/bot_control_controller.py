from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity
from app.shared.domain.models.discord.guild_model import GuildAccessStatus
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from typing import Dict, Optional
from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.sql import func

logger = get_web_logger()
router = APIRouter(prefix="/v1/owner/bot", tags=["Owner Bot Control"])

class AccessUpdateRequest(BaseModel):
    status: str

class BotControlController:
    """Controller for owner bot control functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Bot Control
        self.router.post("/start")(self.start_bot)
        self.router.post("/stop")(self.stop_bot)
        self.router.post("/restart")(self.restart_bot)
        
        # Bot Configuration
        self.router.get("/config")(self.get_bot_config)
        self.router.post("/config")(self.update_bot_config)
        
        # Server Management
        self.router.post("/servers/join/{guild_id}")(self.join_server)
        self.router.post("/servers/leave/{guild_id}")(self.leave_server)
        self.router.post("/servers/{guild_id}/access")(self.update_server_access)
        
        # Workflow Management
        self.router.post("/workflow/{workflow_name}/enable")(self.enable_workflow)
        self.router.post("/workflow/{workflow_name}/disable")(self.disable_workflow)
        
        # Statistics and Overview
        self.router.get("/overview")(self.get_overview_stats)
        self.router.get("/status")(self.get_bot_status)
    
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
    
    async def join_server(self, guild_id: str, current_user=Depends(get_current_user)):
        """Make bot join a specific server"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.join_guild(guild_id)
            return {"message": f"Bot joined server {guild_id} successfully"}
        except Exception as e:
            logger.error(f"Error joining server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def leave_server(self, guild_id: str, current_user=Depends(get_current_user)):
        """Make bot leave a specific server"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            await bot_connector.leave_guild(guild_id)
            return {"message": f"Bot left server {guild_id} successfully"}
        except Exception as e:
            logger.error(f"Error leaving server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_server_access(self, guild_id: str, request: AccessUpdateRequest, current_user=Depends(get_current_user)):
        """Update server access status (approve/deny/block)"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            
            # Get the bot instance
            bot = await bot_connector.get_bot()
            if not bot:
                raise HTTPException(status_code=404, detail="Bot instance not found")
            
            # Get the guild workflow
            guild_workflow = bot.workflow_manager.get_workflow("guild")
            if not guild_workflow:
                raise HTTPException(status_code=404, detail="Guild workflow not found")
            
            # Update access status based on request
            if request.status == "APPROVED":
                success = await guild_workflow.approve_guild(guild_id)
            elif request.status == "DENIED":
                success = await guild_workflow.deny_guild(guild_id)
            elif request.status == "BLOCKED":
                success = await guild_workflow.deny_guild(guild_id)  # Same as deny for now
            else:
                raise HTTPException(status_code=400, detail="Invalid access status")
                
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update guild access status")
            
            return {"message": f"Server {guild_id} access status updated to {request.status}"}
            
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating server access: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_overview_stats(self, current_user=Depends(get_current_user)):
        """Get overview statistics for the bot dashboard"""
        try:
            await require_role(current_user, Role.OWNER)
            
            async with session_context() as session:
                try:
                    # Get statistics from database
                    guilds_query = await session.execute(
                        select(
                            func.count(GuildEntity.id).label('total_guilds'),
                            func.sum(GuildEntity.member_count).label('total_members'),
                            func.count(GuildEntity.id).filter(GuildEntity.is_active == True).label('active_guilds')
                        )
                    )
                    
                    guild_stats = guilds_query.one()
                    
                    stats = {
                        "total_guilds": guild_stats.total_guilds or 0,
                        "total_members": guild_stats.total_members or 0,
                        "active_guilds": guild_stats.active_guilds or 0,
                        "command_count": 0,  # Will be implemented later
                        "recent_commands": 0  # Will be implemented later
                    }
                    
                    return stats
                except Exception as e:
                    logger.error(f"Database error getting statistics: {e}")
                    return {
                        "total_guilds": 0,
                        "total_members": 0,
                        "active_guilds": 0,
                        "command_count": 0,
                        "recent_commands": 0
                    }
        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_bot_status(self, current_user=Depends(get_current_user)):
        """Get current bot status"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            
            # Get bot instance
            bot = await bot_connector.get_bot()
            if not bot:
                return {
                    "status": "offline",
                    "uptime": 0,
                    "active_workflows": [],
                    "available_workflows": []
                }
            
            # Get workflow information
            workflow_manager = bot.workflow_manager
            active_workflows = workflow_manager.get_active_workflows() if workflow_manager else []
            available_workflows = workflow_manager.get_available_workflows() if workflow_manager else []
            
            return {
                "status": "online" if bot.is_ready() else "connecting",
                "uptime": bot.uptime if hasattr(bot, "uptime") else 0,
                "active_workflows": active_workflows,
                "available_workflows": available_workflows,
                "latency": round(bot.latency * 1000, 2) if hasattr(bot, "latency") else 0,
                "guilds": len(bot.guilds) if hasattr(bot, "guilds") else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def enable_workflow(self, workflow_name: str, current_user=Depends(get_current_user)):
        """Enable a specific bot workflow"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            bot = await bot_connector.get_bot()
            
            if not bot:
                raise HTTPException(status_code=404, detail="Bot instance not found")
            
            if not bot.workflow_manager.has_workflow(workflow_name):
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_name} not found")
            
            success = await bot.workflow_manager.enable_workflow(workflow_name)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to enable workflow {workflow_name}")
            
            return {"message": f"Workflow {workflow_name} enabled successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error enabling workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def disable_workflow(self, workflow_name: str, current_user=Depends(get_current_user)):
        """Disable a specific bot workflow"""
        try:
            await require_role(current_user, Role.OWNER)
            bot_connector = await get_bot_connector()
            bot = await bot_connector.get_bot()
            
            if not bot:
                raise HTTPException(status_code=404, detail="Bot instance not found")
            
            if not bot.workflow_manager.has_workflow(workflow_name):
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_name} not found")
            
            success = await bot.workflow_manager.disable_workflow(workflow_name)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to disable workflow {workflow_name}")
            
            return {"message": f"Workflow {workflow_name} disabled successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error disabling workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance and export routes
bot_control_controller = BotControlController()
start_bot = bot_control_controller.start_bot
stop_bot = bot_control_controller.stop_bot
restart_bot = bot_control_controller.restart_bot
get_bot_config = bot_control_controller.get_bot_config
update_bot_config = bot_control_controller.update_bot_config
join_server = bot_control_controller.join_server
leave_server = bot_control_controller.leave_server
get_overview_stats = bot_control_controller.get_overview_stats
get_bot_status = bot_control_controller.get_bot_status
enable_workflow = bot_control_controller.enable_workflow
disable_workflow = bot_control_controller.disable_workflow 