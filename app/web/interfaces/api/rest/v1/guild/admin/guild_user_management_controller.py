from fastapi import APIRouter, Depends, HTTPException, Request
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interfaces.logging.api import get_web_logger
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

# Change the prefix to include guild_id and update tags
router = APIRouter(prefix="/guilds/{guild_id}/users", tags=["Guild Admin: Users"])
logger = get_web_logger()

class GuildUserManagementController:
    """Controller for guild-specific user management"""
    
    ROLE_MAPPING = {
        1: "USER",
        2: "MODERATOR", 
        3: "ADMIN",
        4: "OWNER"
    }

    def __init__(self):
        self.router = router
        self._register_routes()

    def _register_routes(self):
        """Register all routes for guild user management"""
        self.router.get("/{user_id}")(self.get_user_details)
        self.router.put("/{user_id}/role")(self.update_guild_role)
        self.router.put("/{user_id}/app-role")(self.update_app_role)
        self.router.post("/{user_id}/kick")(self.kick_user)

    async def get_user_details(self, guild_id: str, user_id: str, current_user=Depends(get_current_user)):
        """Get detailed information about a guild user"""
        try:
            async with session_context() as session:
                user_data = await self._get_user_details(session, guild_id, user_id)
                if not user_data:
                    raise HTTPException(status_code=404, detail="User not found")
                return user_data
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_guild_role(self, guild_id: str, user_id: str, request: Request, current_user=Depends(get_current_user)):
        """Update a user's guild role"""
        try:
            data = await request.json()
            new_role = data.get("role")
            
            if not await self._can_manage_guild(current_user.id, guild_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._update_guild_role(session, guild_id, user_id, new_role)
                await session.commit()
                
            return {"message": "Role updated successfully"}
        except Exception as e:
            logger.error(f"Error updating guild role: {e}")
            raise HTTPException(status_code=500, detail="Failed to update role")

    async def update_app_role(self, guild_id: str, user_id: str, request: Request, current_user=Depends(get_current_user)):
        """Update a user's app role (requires elevated permissions)"""
        try:
            data = await request.json()
            new_role = data.get("role")
            
            if current_user.role not in ["OWNER", "ADMIN"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._update_app_role(session, user_id, new_role)
                await session.commit()
                
            return {"message": "App role updated successfully"}
        except Exception as e:
            logger.error(f"Error updating app role: {e}")
            raise HTTPException(status_code=500, detail="Failed to update app role")

    async def kick_user(self, guild_id: str, user_id: str, current_user=Depends(get_current_user)):
        """Kick a user from the guild"""
        try:
            if not await self._can_manage_guild(current_user.id, guild_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._kick_user(session, guild_id, user_id)
                await session.commit()
                
            return {"message": "User kicked successfully"}
        except Exception as e:
            logger.error(f"Error kicking user: {e}")
            raise HTTPException(status_code=500, detail="Failed to kick user")

    async def _can_manage_guild(self, user_id: str, guild_id: str) -> bool:
        """Check if user has permission to manage guild users"""
        async with session_context() as session:
            query = select(DiscordGuildUserEntity).where(
                DiscordGuildUserEntity.user_id == user_id,
                DiscordGuildUserEntity.guild_id == guild_id
            )
            result = await session.execute(query)
            guild_user = result.scalar_one_or_none()
            
            return guild_user and guild_user.role_id >= 3  # ADMIN or higher

    async def _get_guild(self, session, guild_id: str):
        """Get guild information"""
        query = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_details(self, session, guild_id: str, user_id: str):
        """Get detailed information about a guild user"""
        query = select(
            DiscordGuildUserEntity,
            AppUserEntity
        ).join(
            AppUserEntity,
            AppUserEntity.id == DiscordGuildUserEntity.user_id
        ).where(
            DiscordGuildUserEntity.guild_id == guild_id,
            DiscordGuildUserEntity.user_id == user_id
        )
        
        result = await session.execute(query)
        guild_user, app_user = result.first()
        
        if not guild_user or not app_user:
            return None
            
        return {
            "id": app_user.id,
            "username": app_user.username,
            "discord_id": app_user.discord_id,
            "guild_role": self._map_role_id_to_name(guild_user.role_id),
            "app_role": self._map_role_id_to_name(app_user.role_id),
            "avatar": app_user.avatar or "default.png",
            "guild_joined_at": guild_user.joined_at.strftime('%Y-%m-%d %H:%M:%S') if guild_user.joined_at else None,
            "last_active": guild_user.last_active.strftime('%Y-%m-%d %H:%M:%S') if guild_user.last_active else None,
            "message_count": guild_user.message_count
        }

    async def _update_guild_role(self, session, guild_id: str, user_id: str, new_role: str):
        """Update a user's guild role"""
        role_id = self._map_role_name_to_id(new_role)
        if not role_id:
            raise HTTPException(status_code=400, detail="Invalid role")
            
        query = select(DiscordGuildUserEntity).where(
            DiscordGuildUserEntity.guild_id == guild_id,
            DiscordGuildUserEntity.user_id == user_id
        )
        result = await session.execute(query)
        guild_user = result.scalar_one_or_none()
        
        if not guild_user:
            raise HTTPException(status_code=404, detail="User not found in guild")
            
        guild_user.role_id = role_id

    async def _update_app_role(self, session, user_id: str, new_role: str):
        """Update a user's app role"""
        role_id = self._map_role_name_to_id(new_role)
        if not role_id:
            raise HTTPException(status_code=400, detail="Invalid role")
            
        query = select(AppUserEntity).where(AppUserEntity.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.role_id = role_id

    async def _kick_user(self, session, guild_id: str, user_id: str):
        """Kick a user from the guild"""
        query = select(DiscordGuildUserEntity).where(
            DiscordGuildUserEntity.guild_id == guild_id,
            DiscordGuildUserEntity.user_id == user_id
        )
        result = await session.execute(query)
        guild_user = result.scalar_one_or_none()
        
        if not guild_user:
            raise HTTPException(status_code=404, detail="User not found in guild")
            
        await session.delete(guild_user)

    @staticmethod
    def _map_role_id_to_name(role_id: int) -> str:
        """Convert role ID to role name"""
        return GuildUserManagementController.ROLE_MAPPING.get(role_id, "UNKNOWN")

    @staticmethod
    def _map_role_name_to_id(role_name: str) -> int:
        """Convert role name to role ID"""
        for role_id, name in GuildUserManagementController.ROLE_MAPPING.items():
            if name == role_name:
                return role_id
        return None

# Create and register the controller
controller = GuildUserManagementController()
# Export the router instance directly
guild_user_management_router = controller.router 
