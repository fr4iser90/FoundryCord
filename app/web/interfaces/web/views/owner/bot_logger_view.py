from fastapi import APIRouter, Request, Depends
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

router = APIRouter()

class BotLoggerView(BaseView):
    """View for displaying the bot logger page."""
    
    def __init__(self, router: APIRouter):
        super().__init__(router)
        self._register_routes()

    def _register_routes(self):
        # Register the route to render the logger page
        self.router.get("/owner/bot/logger", 
                          response_class=self.templates.TemplateResponse,
                          name="owner_bot_logger")(
            self.render_logger_page
        )

    async def render_logger_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render the bot logger index page."""
        # Ensure only owners can access this page
        await self.require_permission(current_user, "OWNER")
        
        self.logger.info(f"User {current_user.username} accessing bot logger page.")
        # Render the specific template for the logger
        return self.render_template(
            "owner/bot/logger/index.html",
            request,
            title="Bot Logs" # Optional: Pass a title
        )

# Initialize the view with the router
bot_logger_view = BotLoggerView(router)
