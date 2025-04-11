from fastapi import APIRouter, Request, Depends
from app.web.core.extensions import templates_extension
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/guilds/users", tags=["Guild User Management"])

logger = get_web_logger()

class GuildUserManagementView:
    """View for guild-specific user management"""
    
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
        self.router.get("", response_class=HTMLResponse)(self.guild_users)

    async def guild_users(self, request: Request):
        """Display guild users with management options"""
        try:
            user = request.session.get("user")
            if not user:
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "error": "Please log in to access this page"}
                )

            active_guild = request.session.get("active_guild")
            if not active_guild:
                return templates.TemplateResponse(
                    "views/errors/404.html",
                    {"request": request, "user": user, "error": "No active guild selected"}
                )
            
            guild_id = active_guild.get("id")
            if not guild_id:
                return templates.TemplateResponse(
                    "views/errors/404.html",
                    {"request": request, "user": user, "error": "Invalid guild selection"}
                )
            
            if not await self._can_manage_guild(user.get("id"), guild_id):
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )

            async with session_context() as session:
                guild = await self._get_guild(session, guild_id)
                if not guild:
                    return templates.TemplateResponse(
                        "views/errors/404.html",
                        {"request": request, "user": user, "error": "Guild not found"}
                    )
                    
                users = await self._get_guild_users(session, guild_id)
                guild_data = {
                    "id": guild.guild_id,
                    "name": guild.name,
                    "roles": await self._get_guild_roles(session, guild_id)
                }
                
                return templates.TemplateResponse(
                    "views/guilds/user_management.html",
                    {
                        "request": request,
                        "user": user,
                        "guild": guild_data,
                        "users": users,
                        "active_page": "guild",
                        "active_section": "users",
                        "can_manage_roles": True,
                        "can_manage_app_roles": user.get("role") in ["OWNER", "ADMIN"],
                        "can_kick_users": True
                    }
                )
        except Exception as e:
            logger.error(f"Error in guild user management: {e}")
            return templates.TemplateResponse(
                "views/errors/500.html",
                {"request": request, "error": str(e)}
            )

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

    async def _get_guild_users(self, session, guild_id: str):
        """Get all users in a guild with their roles"""
        query = select(
            DiscordGuildUserEntity, 
            AppUserEntity
        ).join(
            AppUserEntity,
            AppUserEntity.id == DiscordGuildUserEntity.user_id
        ).where(
            DiscordGuildUserEntity.guild_id == guild_id
        )
        
        result = await session.execute(query)
        users = []
        
        for guild_user, app_user in result:
            users.append({
                "id": app_user.id,
                "username": app_user.username,
                "discord_id": app_user.discord_id,
                "guild_role": self._map_role_id_to_name(guild_user.role_id),
                "app_role": self._map_role_id_to_name(app_user.role_id),
                "avatar": app_user.avatar or "default.png",
                "joined_at": guild_user.joined_at.strftime('%Y-%m-%d %H:%M:%S') if guild_user.joined_at else None,
                "last_active": guild_user.last_active.strftime('%Y-%m-%d %H:%M:%S') if guild_user.last_active else None
            })
        
        return users

    async def _get_guild_roles(self, session, guild_id: str):
        """Get all roles for a guild"""
        query = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
        result = await session.execute(query)
        guild = result.scalar_one_or_none()
        
        if not guild or not guild.roles:
            return []
            
        return [
            {"id": role_id, "name": role_name}
            for role_id, role_name in guild.roles.items()
        ]

    @staticmethod
    def _map_role_id_to_name(role_id: int) -> str:
        """Convert role ID to role name"""
        return GuildUserManagementView.ROLE_MAPPING.get(role_id, "UNKNOWN")

# Create and register the view
view = GuildUserManagementView() 