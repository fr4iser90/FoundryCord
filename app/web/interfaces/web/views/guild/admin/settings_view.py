from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.web.core.extensions import templates_extension
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import AppUserEntity, DiscordGuildUserEntity, GuildEntity
from sqlalchemy import select
from app.shared.interface.logging.api import get_web_logger
from fastapi.responses import HTMLResponse
# Import BaseView for inheritance
from app.web.interfaces.web.views.base_view import BaseView 
# Import dependency for current user
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

# Note: Router instance is now created within the class via BaseView inheritance
logger = get_web_logger()

class GuildAdminSettingsView(BaseView): # Renamed Class, inherits BaseView
    """View for guild admin settings management"""
    
    ROLE_MAPPING = {
        1: "USER",
        2: "MODERATOR", 
        3: "ADMIN",
        4: "OWNER"
    }

    def __init__(self):
        # Pass the correct prefix to the BaseView constructor
        super().__init__(APIRouter(prefix="/guild/{guild_id}/admin/settings", tags=["Guild Admin: Settings"])) 
        self._register_routes()

    def _register_routes(self):
        """Register all routes for guild admin user management"""
        # Route path is now relative to the prefix defined above
        self.router.get("/", response_class=HTMLResponse)(self.render_user_list) 

    # Renamed method and added guild_id path parameter
    async def render_user_list(self, request: Request, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Display guild users with management options for a specific guild."""
        try:
            # Pass the full current_user object to the permission check
            if not await self._can_manage_guild(current_user, guild_id):
                 raise HTTPException(status_code=403, detail="Insufficient permissions for this guild")

            async with session_context() as session:
                # Use guild_id from path parameter
                guild = await self._get_guild(session, guild_id)
                if not guild:
                    # Use error response helper from BaseView
                    return self.error_response(request, "Guild not found", 404)
                    
                # Use guild_id from path parameter
                users = await self._get_guild_users(session, guild_id)
                
                guild_data = {
                    "id": guild.guild_id,
                    "name": guild.name,
                    # Assuming _get_guild_roles is defined in this class or BaseView
                    "roles": await self._get_guild_roles(session, guild_id) 
                }
                
                # Use render_template helper from BaseView and correct path
                return self.render_template(
                    "guild/admin/users.html", # Correct template path
                    request,
                    user=current_user, # Pass the loaded user object
                    guild=guild_data,
                    users=users,
                    active_page="guild-admin", # Suggest more specific active page keys
                    active_section="users",
                    can_manage_roles=True, # Determine these based on current_user permissions if needed
                    can_manage_app_roles=current_user.is_owner or current_user.is_admin, # Example check
                    can_kick_users=True # Example permission
                )
        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to let FastAPI handle them or use error_response
            return self.error_response(request, str(http_exc.detail), http_exc.status_code)
        except Exception as e:
            logger.error(f"Error loading user list for guild {guild_id}: {e}", exc_info=True)
            # Use error response helper from BaseView
            return self.error_response(request, "An unexpected error occurred", 500)

    # --- Helper methods (keep or move to a service/base class) ---

    # Updated to accept the full AppUserEntity for checking global owner status
    async def _can_manage_guild(self, current_user: AppUserEntity, guild_id: str) -> bool:
        """Check if user is Guild Admin/Owner OR Global Bot Owner."""
        
        # 1. Check for Global Bot Owner status first
        if current_user.is_owner:
            logger.debug(f"Granting access to guild {guild_id} for global owner {current_user.id}")
            return True
            
        # 2. If not global owner, check specific guild role
        logger.debug(f"User {current_user.id} is not global owner, checking guild-specific role for {guild_id}")
        async with session_context() as session:
            query = select(DiscordGuildUserEntity).where(
                DiscordGuildUserEntity.user_id == current_user.id, # Use current_user.id
                DiscordGuildUserEntity.guild_id == guild_id
            )
            result = await session.execute(query)
            guild_user = result.scalar_one_or_none()
            
            is_guild_admin_or_owner = guild_user and guild_user.role_id >= 3
            logger.debug(f"User {current_user.id} guild role check for {guild_id}: Found={guild_user is not None}, RoleID={getattr(guild_user, 'role_id', 'N/A')}, Allowed={is_guild_admin_or_owner}")
            return is_guild_admin_or_owner

    async def _get_guild(self, session, guild_id: str):
        """Get guild information"""
        query = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _get_guild_users(self, session, guild_id: str):
        """Get all users in a guild with their roles - SIMPLIFIED QUERY TEST"""
        logger.debug(f"_get_guild_users: Fetching users for guild_id: {guild_id} (Type: {type(guild_id)}) - SIMPLIFIED QUERY")
        
        # --- Simplified Query --- 
        simple_query = select(DiscordGuildUserEntity).where(DiscordGuildUserEntity.guild_id == guild_id)
        logger.debug(f"_get_guild_users: Simplified Query Object: {str(simple_query)}")
        
        guild_user_rows = []
        try:
            logger.info(f"_get_guild_users: Executing simplified query for guild {guild_id}...")
            simple_result = await session.execute(simple_query)
            guild_user_rows = simple_result.scalars().all()
            logger.info(f"_get_guild_users: Simplified query execution finished. Found {len(guild_user_rows)} DiscordGuildUserEntity rows.")
        except Exception as exec_err:
            logger.error(f"_get_guild_users: Error during simplified query execution for guild {guild_id}: {exec_err}", exc_info=True)
            raise
            
        # --- If simplified query fails, return empty --- 
        if not guild_user_rows:
            logger.warning(f"_get_guild_users: Simplified query returned no rows for guild {guild_id}. Returning empty list.")
            return []

        # --- If rows found, fetch AppUser separately (less efficient but for debugging) ---
        logger.info(f"_get_guild_users: Simplified query found {len(guild_user_rows)} rows. Now fetching AppUser details.")
        users = []
        role_mapping = self.ROLE_MAPPING 
        for guild_user_relation in guild_user_rows:
            app_user = await session.get(AppUserEntity, guild_user_relation.user_id)
            if not app_user:
                logger.warning(f"_get_guild_users: Could not find AppUser with ID {guild_user_relation.user_id} for guild {guild_id}")
                continue # Skip this user if AppUser record is missing

            users.append({
                "id": app_user.id,
                "username": app_user.username,
                "discord_id": app_user.discord_id,
                "guild_role": role_mapping.get(guild_user_relation.role_id, "UNKNOWN"),
                "guild_role_id": guild_user_relation.role_id,
                "app_role": role_mapping.get(getattr(app_user, 'role_id', guild_user_relation.role_id), "UNKNOWN"),
                "avatar": app_user.avatar or "/static/img/default_avatar.png",
            })
        
        logger.debug(f"_get_guild_users: Returning {len(users)} processed users for guild {guild_id}.")
        return users

    async def _get_guild_roles(self, session, guild_id: str) -> list:
        """Get all roles for a guild.
        
        NOTE: Roles are not stored directly on the GuildEntity in the current schema.
              Fetching live roles requires interacting with the Discord API (likely via the bot).
              Returning empty list to prevent errors in the template's role dropdown.
              Role editing functionality will need a different implementation.
        """
        logger.debug(f"_get_guild_roles called for {guild_id}. Returning empty list as roles are not stored in DB.")
        # Return an empty list as roles are not stored on GuildEntity
        return [] 
        
        # --- Old Placeholder Logic (Removed) ---
        # guild = await self._get_guild(session, guild_id)
        # if not guild or not isinstance(guild.roles, dict):
        #      return [] 
        # return [{"id": role_id, "name": role_name} for role_id, role_name in guild.roles.items()]

    # Removed static methods for role mapping, use self.ROLE_MAPPING

# Create and register the view instance
guild_admin_settings_view = GuildAdminSettingsView()
# Export the router from the instance
router = guild_admin_settings_view.router 