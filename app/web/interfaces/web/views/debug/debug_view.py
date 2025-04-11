from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.interfaces.web.views.base_view import BaseView

class DebugView(BaseView):
    def __init__(self):
        super().__init__(APIRouter(prefix="/debug", tags=["Debug"]))
        self._register_routes()

    def _register_routes(self):
        self.router.get("/")(self.debug_home)
        self.router.get("/add-test-guild-form")(self.add_test_guild_form)

    async def debug_home(self, request: Request, current_user=Depends(get_current_user)):
        """Debug home page with links to all debug functions"""
        return self.render_template(
            "debug/debug_home.html", 
            request,
            user=current_user
        )

    async def add_test_guild_form(self, request: Request, current_user=Depends(get_current_user)):
        """Form to add a test guild"""
        return self.render_template(
            "debug/add_test_guild.html", 
            request,
            user=current_user
        )

# View instance
debug_view = DebugView()
router = debug_view.router