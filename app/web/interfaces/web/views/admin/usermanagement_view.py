from fastapi import APIRouter, Request
from app.web.core.extensions import get_templates
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/admin/users", tags=["User Management"])
templates = get_templates()
logger = get_web_logger()

class UserManagementView:
    """Separate view class for user management functionality"""
    
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
        self.router.get("", response_class=HTMLResponse)(self.user_management)
        self.router.get("/{user_id}/roles", response_class=JSONResponse)(self.get_user_roles)
        self.router.put("/{user_id}/role", response_class=JSONResponse)(self.update_user_role)

    @staticmethod
    def _map_role_id_to_name(role_id: int) -> str:
        return UserManagementView.ROLE_MAPPING.get(role_id, "USER")

    async def user_management(self, request: Request):
        """User management page with app roles and read-only guild roles"""
        try:
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER"]:
                return templates.TemplateResponse(
                    "pages/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )

            async with session_context() as session:
                users = await self._get_users_with_roles(session)
                
                return templates.TemplateResponse(
                    "pages/admin/user_management.html",
                    {
                        "request": request,
                        "user": user,
                        "users": users,
                        "active_page": "admin-users"
                    }
                )
        except Exception as e:
            logger.error(f"Error in user management: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "error": str(e)}
            )

    async def _get_users_with_roles(self, session):
        """Helper to get all users with their roles"""
        query = select(AppUserEntity)
        result = await session.execute(query)
        db_users = result.scalars().all()

        users = []
        for db_user in db_users:
            guild_roles = await self._get_user_guild_roles(session, db_user.id)
            
            users.append({
                "id": db_user.id,
                "username": db_user.username,
                "discord_id": db_user.discord_id,
                "app_role": self._map_role_id_to_name(db_user.role_id),
                "is_active": db_user.is_active,
                "guilds": guild_roles,
                "avatar": db_user.avatar or "default.png"
            })
        
        return users

    async def _get_user_guild_roles(self, session, user_id):
        """Helper to get user's guild roles (read-only)"""
        query = select(DiscordGuildUserEntity, GuildEntity).join(
            GuildEntity,
            GuildEntity.guild_id == DiscordGuildUserEntity.guild_id
        ).where(DiscordGuildUserEntity.user_id == user_id)
        
        result = await session.execute(query)
        guild_roles = []
        
        for guild_user, guild in result:
            guild_roles.append({
                "guild_name": guild.name,
                "role": guild_user.role_id
            })
            
        return guild_roles
