from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import templates_extension
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.interface.logging.api import get_web_logger
from app.web.infrastructure.config.env_loader import get_discord_oauth_config
from app.shared.infrastructure.constants import OWNER, ADMINS, MODERATORS, USERS
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from sqlalchemy import select
import httpx

router = APIRouter(prefix="/auth", tags=["Authentication Views"])
templates = templates_extension()
logger = get_web_logger()
discord_config = get_discord_oauth_config()

class AuthView:
    """View for authentication pages and OAuth flow"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register web routes"""
        self.router.get("/login", response_class=HTMLResponse)(self.login_page)
        self.router.get("/callback")(self.oauth_callback)
        self.router.get("/logout", response_class=HTMLResponse)(self.logout_page)
        self.router.get("/discord-login")(self.discord_login)  # New route for Discord redirect
    
    async def login_page(self, request: Request):
        """Render login page"""
        if "user" in request.session:
            return RedirectResponse(url="/home")
            
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "page_title": "Login - HomeLab Discord Bot"
            }
        )

    async def discord_login(self, request: Request):
        """Generate Discord OAuth URL and redirect"""
        logger.debug(f"Using OAuth config: {discord_config}")  # Log config for debugging
        auth_url = (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={discord_config['client_id']}"
            f"&redirect_uri={discord_config['redirect_uri']}"
            f"&response_type=code"
            f"&scope=identify"
        )
        logger.debug(f"Generated auth URL: {auth_url}")  # Log URL for debugging
        return RedirectResponse(url=auth_url)

    async def oauth_callback(self, code: str, request: Request):
        """Handle OAuth callback from Discord"""
        try:
            logger.debug(f"Received callback with code: {code}")  # Log callback
            async with httpx.AsyncClient() as client:
                token_data = {
                    "client_id": discord_config["client_id"],
                    "client_secret": discord_config["client_secret"],
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": discord_config["redirect_uri"]
                }
                logger.debug(f"Token exchange data: {token_data}")  # Log exchange data
                # Exchange code for token
                token_response = await client.post(
                    "https://discord.com/api/oauth2/token",
                    data=token_data
                )
                
                if token_response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Failed to authenticate with Discord")
                
                token = token_response.json()
                
                # Get user info
                user_response = await client.get(
                    "https://discord.com/api/users/@me",
                    headers={"Authorization": f"Bearer {token['access_token']}"}
                )
                
                if user_response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Failed to get user information")
                
                user_data = user_response.json()
                user_id = user_data["id"]
                
                # Determine user role
                if str(user_id) in OWNER.values():
                    user_role = "OWNER"
                elif str(user_id) in ADMINS.values():
                    user_role = "ADMIN"
                elif str(user_id) in MODERATORS.values():
                    user_role = "MODERATOR"
                elif str(user_id) in USERS.values():
                    user_role = "USER"
                else:
                    user_role = "GUEST"
                
                # Create session user
                user = {
                    "id": user_id,
                    "username": user_data["username"],
                    "avatar": user_data.get("avatar"),
                    "discriminator": user_data.get("discriminator", "0000"),
                    "role": user_role
                }
                
                # Get first available guild and set as active
                async with session_context() as session:
                    result = await session.execute(select(GuildEntity))
                    first_guild = result.scalars().first()
                    
                    if first_guild:
                        request.session["active_guild"] = {
                            "id": first_guild.guild_id,
                            "name": first_guild.name,
                            "icon_url": first_guild.icon_url or "https://cdn.discordapp.com/embed/avatars/0.png"
                        }
                
                request.session["user"] = user
                request.session["token"] = token["access_token"]
                
                return RedirectResponse(url="/home", status_code=303)
                
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            return RedirectResponse(url="/auth/login", status_code=303)
    
    async def logout_page(self, request: Request):
        """Handle web logout and render logout page"""
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)

# Create view instance
auth_view = AuthView()
login_page = auth_view.login_page
oauth_callback = auth_view.oauth_callback
logout_page = auth_view.logout_page
discord_login = auth_view.discord_login 