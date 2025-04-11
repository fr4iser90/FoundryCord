from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
# Import the correct dependency
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class DebugController(BaseController):
    """Controller for debug functionality"""
    
    def __init__(self):
        super().__init__(prefix="/debug", tags=["Debug"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all debug routes"""
        self.router.get("/guilds")(self.debug_guilds)
        self.router.post("/add-test-guild")(self.add_test_guild)
        self.router.get("/db-status")(self.debug_db_status)
        self.router.post("/add-test-guild-with-details")(self.add_test_guild_with_details)
        self.router.get("/check-schema")(self.check_schema)
    
    async def debug_guilds(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Debug endpoint to display all guilds in the database"""
        try:
            guilds = await self.debug_service.get_all_guilds()
            return self.success_response(guilds)
        except Exception as e:
            return self.handle_exception(e)
    
    async def add_test_guild(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Adds a test guild to the database"""
        try:
            result = await self.debug_service.add_test_guild()
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def debug_db_status(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Debug endpoint to display database status"""
        try:
            status = await self.debug_service.get_db_status()
            return self.success_response(status)
        except Exception as e:
            return self.handle_exception(e)
    
    async def add_test_guild_with_details(
        self,
        guild_id: str,
        name: str,
        icon_url: str = "https://cdn.discordapp.com/embed/avatars/0.png",
        member_count: int = 21,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Adds a custom test guild to the database"""
        try:
            result = await self.debug_service.add_test_guild_with_details(
                guild_id=guild_id,
                name=name,
                icon_url=icon_url,
                member_count=member_count
            )
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def check_schema(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Checks if the database schema is correct"""
        try:
            schema = await self.debug_service.check_schema()
            return self.success_response(schema)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
debug_controller = DebugController()
