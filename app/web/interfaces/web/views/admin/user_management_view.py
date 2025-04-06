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
            logger.debug(f"Current user from session: {user}")
            
            if not user or user.get("role") not in ["OWNER", "ADMIN", "MODERATOR"]:
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )

            # Get current guild from session
            current_guild = request.session.get("active_guild")
            logger.debug(f"Current guild from session: {current_guild}")
            
            if not current_guild:
                return templates.TemplateResponse(
                    "views/errors/400.html",
                    {"request": request, "error": "No guild selected"}
                )

            async with session_context() as session:
                # Get guild users with roles
                users = await self._get_guild_users(session, current_guild["id"])
                
                # Debug log
                logger.debug(f"Found {len(users)} users for guild {current_guild['name']}")
                
                # Get guild roles
                guild_roles = [
                    {"id": "USER", "name": "User"},
                    {"id": "MODERATOR", "name": "Moderator"},
                    {"id": "ADMIN", "name": "Admin"},
                    {"id": "OWNER", "name": "Owner"}
                ]
                
                return templates.TemplateResponse(
                    "views/admin/users.html",
                    {
                        "request": request,
                        "user": user,
                        "users": users,
                        "current_guild": current_guild,
                        "guild_roles": guild_roles,
                        "active_page": "admin",
                        "active_section": "users",
                        "can_manage_role": self.can_manage_role,
                        "can_manage_status": self.can_manage_status,
                        "can_manage_user": lambda u, cu: cu.get("role") in ["OWNER", "ADMIN"] or 
                                                      (cu.get("role") == "MODERATOR" and u.get("app_role") == "USER"),
                        "current_user": user
                    }
                )
        except Exception as e:
            logger.error(f"Error in user management: {e}")
            logger.exception("Full traceback:")
            return templates.TemplateResponse(
                "views/errors/500.html",
                {"request": request, "error": str(e)}
            )

    async def _get_guild_users(self, session, guild_id: str) -> list:
        """Get users for a specific guild with their roles"""
        try:
            logger.debug(f"Fetching users for guild {guild_id}")
            
            # First check if guild exists
            guild_query = select(GuildEntity).where(GuildEntity.guild_id == str(guild_id))
            guild = await session.execute(guild_query)
            guild = guild.scalar()
            logger.debug(f"Found guild: {guild.name if guild else 'None'}")
            
            # Debug: Print the query we're about to execute
            query = select(
                DiscordGuildUserEntity,
                AppUserEntity
            ).join(
                AppUserEntity,
                DiscordGuildUserEntity.user_id == AppUserEntity.id
            ).where(
                DiscordGuildUserEntity.guild_id == str(guild_id)
            )
            logger.debug(f"SQL Query: {query}")
            
            # Execute query and get raw result for debugging
            result = await session.execute(query)
            raw_result = result.fetchall()
            logger.debug(f"Raw query result: {raw_result}")
            
            users = []
            for guild_user, user in raw_result:
                logger.debug(f"Processing user: {user.username} (ID: {user.id}) with role {user.role_id}")
                logger.debug(f"User details: avatar={user.avatar}, discord_id={user.discord_id}")
                logger.debug(f"Guild user details: role_id={guild_user.role_id}, created_at={guild_user.created_at}")
                
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "discord_id": user.discord_id,
                    "app_role": self._map_role_id_to_name(user.role_id),
                    "guild_role": guild_user.role_id,
                    "is_active": user.is_active,
                    "avatar": user.avatar or "https://cdn.discordapp.com/embed/avatars/0.png",
                    "last_active": self._format_datetime(user.last_login),
                    "joined_at": self._format_datetime(guild_user.created_at)
                })
            
            logger.debug(f"Returning {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching guild users: {e}")
            logger.exception("Full traceback:")
            return []

    async def get_user_details(self, request: Request, user_id: str):
        """Get detailed information about a user in the current guild"""
        try:
            current_guild = request.session.get("active_guild")
            if not current_guild:
                raise HTTPException(status_code=400, detail="No guild selected")

            async with session_context() as session:
                user_data = await self._get_user_guild_details(session, user_id, current_guild["id"])
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
            current_guild = request.session.get("active_guild")
            
            if not current_guild:
                raise HTTPException(status_code=400, detail="No guild selected")
            
            current_user = request.session.get("user")
            if not self.can_manage_role({"id": user_id}, current_user):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            async with session_context() as session:
                await self._update_user_role(session, user_id, current_guild["id"], new_role)
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
            current_guild = request.session.get("active_guild")
            
            if not current_guild:
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