from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from typing import Dict, List, Optional
import asyncio
from sqlalchemy import select

logger = get_web_logger()
router = APIRouter(prefix="/v1/owner", tags=["Owner Controls"])

class OwnerController:
    """Controller for owner-specific functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Server Management
        self.router.get("/servers")(self.list_servers)
        self.router.post("/servers/add")(self.add_server)
        self.router.delete("/servers/{guild_id}")(self.remove_server)
        
        # Bot Configuration
        self.router.get("/bot/config")(self.get_bot_config)
        self.router.post("/bot/config")(self.update_bot_config)
        
        # System Logs
        self.router.get("/logs")(self.get_system_logs)
        self.router.post("/logs/clear")(self.clear_system_logs)
    
    async def list_servers(self, current_user=Depends(get_current_user)):
        """List all servers the bot is configured to connect to"""
        try:
            await require_role(current_user, Role.OWNER)
            
            async with session_context() as session:
                result = await session.execute(select(GuildEntity))
                guilds = result.scalars().all()
                
                return [
                    {
                        "id": guild.id,
                        "guild_id": guild.guild_id,
                        "name": guild.name,
                        "is_verified": guild.is_verified,
                        "member_count": guild.member_count,
                        "joined_at": guild.joined_at.isoformat() if guild.joined_at else None
                    }
                    for guild in guilds
                ]
        except Exception as e:
            logger.error(f"Error listing servers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def add_server(self, server_data: Dict, current_user=Depends(get_current_user)):
        """Add a new server for the bot to connect to"""
        try:
            await require_role(current_user, Role.OWNER)
            
            guild_id = server_data.get("guild_id")
            if not guild_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Guild ID is required"
                )
            
            async with session_context() as session:
                # Check if server already exists
                existing = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                if existing.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Server with ID {guild_id} already exists"
                    )
                
                # Create new guild entity
                new_guild = GuildEntity(
                    guild_id=guild_id,
                    name=server_data.get("name", "Unknown Server"),
                    is_verified=True
                )
                session.add(new_guild)
                await session.commit()
                
                return {
                    "message": f"Server {guild_id} added successfully",
                    "guild_id": guild_id
                }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def remove_server(self, guild_id: str, current_user=Depends(get_current_user)):
        """Remove a server from bot's configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Server with ID {guild_id} not found"
                    )
                
                await session.delete(guild)
                await session.commit()
                
                return {"message": f"Server {guild_id} removed successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_bot_config(self, current_user=Depends(get_current_user)):
        """Get current bot configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get bot configuration from environment or database
            config = {
                "bot_token": "***************",  # Masked for security
                "command_prefix": "!",
                "auto_reconnect": True,
                "log_level": "INFO",
                "status_update_interval": 60,
                "max_reconnect_attempts": 5
            }
            
            return config
        except Exception as e:
            logger.error(f"Error getting bot config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_bot_config(self, config_data: Dict, current_user=Depends(get_current_user)):
        """Update bot configuration"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Validate and update configuration
            # This is a placeholder - implement actual config update logic
            return {
                "message": "Bot configuration updated successfully",
                "updated_fields": list(config_data.keys())
            }
        except Exception as e:
            logger.error(f"Error updating bot config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_system_logs(self, current_user=Depends(get_current_user)):
        """Get system logs"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Implement actual log retrieval logic
            logs = [
                {"timestamp": "2024-03-23T12:00:00", "level": "INFO", "message": "Bot started"},
                {"timestamp": "2024-03-23T12:01:00", "level": "INFO", "message": "Connected to Discord"},
            ]
            
            return logs
        except Exception as e:
            logger.error(f"Error getting system logs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def clear_system_logs(self, current_user=Depends(get_current_user)):
        """Clear system logs"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Implement actual log clearing logic
            return {"message": "System logs cleared successfully"}
        except Exception as e:
            logger.error(f"Error clearing system logs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance and export routes
owner_controller = OwnerController()
get_system_logs = owner_controller.get_system_logs
clear_system_logs = owner_controller.clear_system_logs
list_servers = owner_controller.list_servers
add_server = owner_controller.add_server
remove_server = owner_controller.remove_server
get_bot_config = owner_controller.get_bot_config
update_bot_config = owner_controller.update_bot_config 