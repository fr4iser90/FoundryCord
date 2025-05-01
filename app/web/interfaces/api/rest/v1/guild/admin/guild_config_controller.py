from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.application.services.template.template_service import GuildTemplateService

class GuildConfigController(BaseController):
    """Controller for guild configuration functionality"""
    
    def __init__(self):
        super().__init__(prefix="/guilds", tags=["Guild Configuration"])
        self.guild_service = GuildTemplateService()
        self._register_routes()
    
    def _register_routes(self):
        """Register all guild configuration routes"""
        self.router.get("/{guild_id}/config")(self.get_guild_config)
        self.router.put("/{guild_id}/config")(self.update_guild_config)
        self.router.get("/{guild_id}/permissions")(self.get_guild_permissions)
        self.router.put("/{guild_id}/permissions")(self.update_guild_permissions)
    
    async def get_guild_config(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get guild configuration"""
        try:
            config = await self.guild_service.get_guild_config(guild_id)
            return self.success_response(config)
        except Exception as e:
            return self.handle_exception(e)
    
    async def update_guild_config(self, guild_id: str, config: dict, current_user: AppUserEntity = Depends(get_current_user)):
        """Update guild configuration"""
        try:
            updated_config = await self.guild_service.update_guild_config(guild_id, config)
            return self.success_response(updated_config)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_guild_permissions(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get guild permissions"""
        try:
            permissions = await self.guild_service.get_guild_permissions(guild_id)
            return self.success_response(permissions)
        except Exception as e:
            return self.handle_exception(e)
    
    async def update_guild_permissions(self, guild_id: str, permissions: dict, current_user: AppUserEntity = Depends(get_current_user)):
        """Update guild permissions"""
        try:
            updated_permissions = await self.guild_service.update_guild_permissions(guild_id, permissions)
            return self.success_response(updated_permissions)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
guild_config_controller = GuildConfigController() 