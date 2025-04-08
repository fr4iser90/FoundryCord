from fastapi import APIRouter, Request, HTTPException
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

router = router = APIRouter(prefix="/admin/users", tags=["Admin User Management"])
logger = get_web_logger()

class UserManagementController:
    """Controller for admin user management functionality"""
    
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
        """Register all routes for user management"""
        self.router.get("/{user_id}")(self.get_user_details)
        self.router.put("/{user_id}/role")(self.update_user_role)
        self.router.put("/{user_id}/status")(self.update_user_status)
        self.router.delete("/{user_id}")(self.delete_user)

    def _format_datetime(self, dt):
        """Safely format datetime objects"""
        if dt is None:
            return None
        return dt.isoformat() if isinstance(dt, datetime) else dt

    def _format_user_details(self, user: AppUserEntity, guild_user: DiscordGuildUserEntity = None) -> Dict[str, Any]:
        """Format user details for API response"""
        details = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": self._format_datetime(user.created_at),
            "last_login": self._format_datetime(user.last_login)
        }
        
        if guild_user:
            details.update({
                "guild_role": self.ROLE_MAPPING.get(guild_user.role_id, "UNKNOWN"),
                "joined_at": self._format_datetime(guild_user.joined_at),
                "last_active": self._format_datetime(guild_user.last_active)
            })
        
        return details

    async def get_user_details(self, request: Request, user_id: str):
        """Get detailed information about a user"""
        try:
            current_guild = request.session.get("active_guild")
            if not current_guild:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            async with session_context() as session:
                user = await session.get(AppUserEntity, user_id)
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                guild_user = await session.get(
                    DiscordGuildUserEntity, 
                    (user_id, current_guild["id"])
                )
                
                return self._format_user_details(user, guild_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            raise HTTPException(status_code=500, detail="Failed to get user details")

    async def update_user_role(self, request: Request, user_id: str):
        """Update a user's role in the current guild"""
        try:
            current_guild = request.session.get("active_guild")
            if not current_guild:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            data = await request.json()
            new_role = data.get("role")
            if not new_role:
                raise HTTPException(status_code=400, detail="Role not specified")
            
            async with session_context() as session:
                await self._update_user_role(session, user_id, current_guild["id"], new_role)
                await session.commit()
                
            return JSONResponse(content={"message": "User role updated successfully"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            raise HTTPException(status_code=500, detail="Failed to update user role")

    async def update_user_status(self, request: Request, user_id: str):
        """Update a user's active status"""
        try:
            data = await request.json()
            is_active = data.get("is_active")
            if is_active is None:
                raise HTTPException(status_code=400, detail="Active status not specified")
            
            async with session_context() as session:
                await self._update_user_status(session, user_id, is_active)
                await session.commit()
                
            return JSONResponse(content={"message": "User status updated successfully"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            raise HTTPException(status_code=500, detail="Failed to update user status")

    async def delete_user(self, request: Request, user_id: str):
        """Remove a user from the current guild"""
        try:
            current_guild = request.session.get("active_guild")
            if not current_guild:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            current_user = request.session.get("user")
            if not self.can_manage_role({"id": user_id}, current_user):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._remove_user_from_guild(session, user_id, current_guild["id"])
                await session.commit()
                
            return JSONResponse(content={"message": "User removed from guild successfully"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing user from guild: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove user")

    async def _update_user_role(self, session, user_id: str, guild_id: str, new_role: str):
        """Update a user's role in a specific guild"""
        guild_user = await session.get(DiscordGuildUserEntity, (user_id, guild_id))
        if not guild_user:
            raise HTTPException(status_code=404, detail="User not found in guild")
        
        guild_user.role_id = new_role
        session.add(guild_user)

    async def _update_user_status(self, session, user_id: str, is_active: bool):
        """Update a user's active status"""
        user = await session.get(AppUserEntity, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = is_active
        session.add(user)

    async def _remove_user_from_guild(self, session, user_id: str, guild_id: str):
        """Remove a user from a specific guild"""
        guild_user = await session.get(DiscordGuildUserEntity, (user_id, guild_id))
        if guild_user:
            await session.delete(guild_user)

    def can_manage_role(self, target_user: Dict[str, Any], current_user: Dict[str, Any]) -> bool:
        """Check if current user can manage the target user's role"""
        if not current_user or not target_user:
            return False
            
        current_role = current_user.get("role", 0)
        target_role = target_user.get("role", 0)
        
        # Users can't manage themselves
        if current_user["id"] == target_user["id"]:
            return False
            
        # Higher role can manage lower roles
        return current_role > target_role

# Controller instance
user_management_controller = UserManagementController() 