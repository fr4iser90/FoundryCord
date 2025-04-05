from fastapi import APIRouter, Request, HTTPException
from app.web.core.extensions import templates_extension, time_extension
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/admin/users", tags=["Server User Management"])
templates = templates_extension()
logger = get_web_logger()

class UserManagementView:
    """View for server-specific user management"""
    
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
        self.router.get("", response_class=HTMLResponse)(self.user_management)
        self.router.get("/{user_id}", response_class=JSONResponse)(self.get_user_details)
        self.router.put("/{user_id}/role", response_class=JSONResponse)(self.update_user_role)
        self.router.put("/{user_id}/status", response_class=JSONResponse)(self.update_user_status)
        self.router.delete("/{user_id}", response_class=JSONResponse)(self.delete_user)

    def _format_datetime(self, dt):
        """Safely format datetime objects"""
        if dt is None:
            return None
        return dt.isoformat() if isinstance(dt, datetime) else dt

    def can_manage_role(self, target_user: Dict[str, Any], current_user: Dict[str, Any]) -> bool:
        """Check if current user can manage target user's role"""
        if current_user.get("role") == "OWNER":
            return True
        if current_user.get("role") == "ADMIN":
            return target_user.get("app_role") not in ["ADMIN", "OWNER"]
        return False

    def can_manage_status(self, target_user: Dict[str, Any], current_user: Dict[str, Any]) -> bool:
        """Check if current user can manage target user's status"""
        if current_user.get("role") == "OWNER":
            return True
        if current_user.get("role") == "ADMIN":
            return target_user.get("app_role") not in ["ADMIN", "OWNER"]
        if current_user.get("role") == "MODERATOR":
            return target_user.get("app_role") == "USER"
        return False

    async def user_management(self, request: Request):
        """Server-specific user management page"""
        try:
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER", "ADMIN", "MODERATOR"]:
                return templates.TemplateResponse(
                    "pages/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )

            guild_id = request.query_params.get("guild_id")
            if not guild_id:
                return templates.TemplateResponse(
                    "pages/errors/400.html",
                    {"request": request, "error": "No guild selected"}
                )

            async with session_context() as session:
                # Get current guild
                guild = await self._get_guild(session, guild_id)
                if not guild:
                    return templates.TemplateResponse(
                        "pages/errors/404.html",
                        {"request": request, "error": "Guild not found"}
                    )

                # Get guild users with roles
                users = await self._get_guild_users(session, guild_id)
                
                return templates.TemplateResponse(
                    "pages/admin/user_management.html",
                    {
                        "request": request,
                        "user": user,
                        "users": users,
                        "current_guild": guild,
                        "guild_roles": await self._get_guild_roles(session, guild_id),
                        "active_page": "admin",
                        "active_section": "users",
                        "can_manage_role": self.can_manage_role,
                        "can_manage_status": self.can_manage_status
                    }
                )
        except Exception as e:
            logger.error(f"Error in user management: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "error": str(e)}
            )

    async def _get_guild(self, session, guild_id: str) -> Dict[str, Any]:
        """Get guild information"""
        query = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
        result = await session.execute(query)
        guild = result.scalar_one_or_none()
        
        if not guild:
            return None
            
        return {
            "id": guild.guild_id,
            "name": guild.name,
            "icon": guild.icon
        }

    async def _get_guild_roles(self, session, guild_id: str) -> list:
        """Get available roles for the guild"""
        # This would be replaced with actual Discord role fetching
        return [
            {"id": "user", "name": "User"},
            {"id": "moderator", "name": "Moderator"},
            {"id": "admin", "name": "Admin"}
        ]

    async def _get_guild_users(self, session, guild_id: str) -> list:
        """Get users for a specific guild with their roles"""
        query = select(
            AppUserEntity,
            DiscordGuildUserEntity
        ).join(
            DiscordGuildUserEntity,
            DiscordGuildUserEntity.user_id == AppUserEntity.id
        ).where(
            DiscordGuildUserEntity.guild_id == guild_id
        )
        
        result = await session.execute(query)
        users = []
        
        for user, guild_user in result:
            users.append({
                "id": user.id,
                "username": user.username,
                "discord_id": user.discord_id,
                "app_role": self._map_role_id_to_name(user.role_id),
                "guild_role": guild_user.role_id,
                "is_active": user.is_active,
                "avatar": user.avatar,
                "last_active": self._format_datetime(user.last_login),
                "joined_at": self._format_datetime(guild_user.joined_at)
            })
        
        return users

    async def get_user_details(self, request: Request, user_id: str):
        """Get detailed information about a user in the current guild"""
        try:
            guild_id = request.query_params.get("guild_id")
            if not guild_id:
                raise HTTPException(status_code=400, detail="No guild selected")

            async with session_context() as session:
                user_data = await self._get_user_guild_details(session, user_id, guild_id)
                if not user_data:
                    raise HTTPException(status_code=404, detail="User not found")
                return JSONResponse(content=user_data)
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def _get_user_guild_details(self, session, user_id: str, guild_id: str):
        """Get detailed information about a user in a specific guild"""
        query = select(
            AppUserEntity,
            DiscordGuildUserEntity
        ).join(
            DiscordGuildUserEntity,
            DiscordGuildUserEntity.user_id == AppUserEntity.id
        ).where(
            AppUserEntity.id == user_id,
            DiscordGuildUserEntity.guild_id == guild_id
        )
        
        result = await session.execute(query)
        user, guild_user = result.first()
        
        if not user:
            return None
            
        return {
            "id": user.id,
            "username": user.username,
            "discord_id": user.discord_id,
            "app_role": self._map_role_id_to_name(user.role_id),
            "guild_role": guild_user.role_id,
            "is_active": user.is_active,
            "avatar": user.avatar,
            "created_at": self._format_datetime(user.created_at),
            "last_login": self._format_datetime(user.last_login),
            "joined_at": self._format_datetime(guild_user.joined_at),
            "last_active": self._format_datetime(guild_user.last_active)
        }

    @staticmethod
    def _map_role_id_to_name(role_id: int) -> str:
        return UserManagementView.ROLE_MAPPING.get(role_id, "USER")

    async def update_user_role(self, request: Request, user_id: str):
        """Update a user's role in the current guild"""
        try:
            data = await request.json()
            new_role = data.get("role")
            guild_id = request.query_params.get("guild_id")
            
            if not guild_id:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            current_user = request.session.get("user")
            if not self.can_manage_role({"id": user_id}, current_user):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._update_user_role(session, user_id, guild_id, new_role)
                await session.commit()
                
            return JSONResponse(content={"message": "Role updated successfully"})
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            raise HTTPException(status_code=500, detail="Failed to update role")

    async def update_user_status(self, request: Request, user_id: str):
        """Update a user's status"""
        try:
            data = await request.json()
            is_active = data.get("is_active")
            guild_id = request.query_params.get("guild_id")
            
            if not guild_id:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            current_user = request.session.get("user")
            if not self.can_manage_status({"id": user_id}, current_user):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._update_user_status(session, user_id, is_active)
                await session.commit()
                
            return JSONResponse(content={"message": "Status updated successfully"})
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            raise HTTPException(status_code=500, detail="Failed to update status")

    async def delete_user(self, request: Request, user_id: str):
        """Remove a user from the current guild"""
        try:
            guild_id = request.query_params.get("guild_id")
            if not guild_id:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            current_user = request.session.get("user")
            if not self.can_manage_role({"id": user_id}, current_user):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._remove_user_from_guild(session, user_id, guild_id)
                await session.commit()
                
            return JSONResponse(content={"message": "User removed from guild successfully"})
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
        if not guild_user:
            raise HTTPException(status_code=404, detail="User not found in guild")
        
        await session.delete(guild_user)

# Create view instance
user_management_view = UserManagementView() 