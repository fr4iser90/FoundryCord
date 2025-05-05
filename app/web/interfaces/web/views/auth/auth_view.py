from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.interfaces.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from sqlalchemy import select
import httpx
from app.web.infrastructure.config.env_loader import get_discord_oauth_config
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory

router = APIRouter(prefix="/auth", tags=["Authentication Views"])

logger = get_web_logger()
discord_config = get_discord_oauth_config()

class AuthView(BaseView):
    """View for authentication pages and OAuth flow"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/auth", tags=["Authentication"]))
        self._register_routes()
    
    def _register_routes(self):
        """Register web routes"""
        self.router.get("/login", response_class=HTMLResponse)(self.login_page)
        self.router.get("/callback")(self.oauth_callback)
        self.router.get("/logout", response_class=HTMLResponse)(self.logout_page)
        self.router.get("/discord-login")(self.discord_login)
    
    async def login_page(self, request: Request):
        """Render login page"""
        if "user" in request.session:
            return RedirectResponse(url="/home")
            
        return self.render_template(
            "auth/login.html",
            request,
            page_title="Login - HomeLab Discord Bot"
        )

    async def discord_login(self, request: Request):
        """Generate Discord OAuth URL and redirect"""
        self.logger.debug(f"Using OAuth config: {discord_config}")
        auth_url = (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={discord_config['client_id']}"
            f"&redirect_uri={discord_config['redirect_uri']}"
            f"&response_type=code"
            f"&scope=identify"
        )
        self.logger.debug(f"Generated auth URL: {auth_url}")
        return RedirectResponse(url=auth_url)

    async def oauth_callback(self, code: str, request: Request):
        """Handle OAuth callback from Discord"""
        try:
            self.logger.debug(f"Received callback with code: {code}")
            user_data = await self.auth_service.handle_oauth_callback(code)
            
            if not user_data:
                return RedirectResponse(url="/auth/login", status_code=303)
            
            # Store only basic user data in session
            request.session["user"] = {
                "id": user_data["id"],
                "username": user_data["username"],
                "discord_id": user_data["discord_id"],
                "is_owner": user_data.get("is_owner", False),
                "avatar": user_data.get("avatar")
                # Permissions removed as they are not directly available here
            }
            
            self.logger.info(f"User {user_data['username']} logged in.") # Simplified log message
            return RedirectResponse(url="/home", status_code=303)
                
        except HTTPException as e:
            self.logger.error(f"OAuth callback failed with HTTP error: {e}")
            return RedirectResponse(url="/auth/login", status_code=303)
        except Exception as e:
            self.logger.error(f"OAuth callback failed with unexpected error: {e}")
            return RedirectResponse(url="/auth/login", status_code=303)
    
    async def logout_page(self, request: Request):
        """Handle web logout and render logout page"""
        try:
            request.session.clear()
            return RedirectResponse(url="/", status_code=303)
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return RedirectResponse(url="/", status_code=303)

# View instance und Export
auth_view = AuthView()
router = auth_view.router 