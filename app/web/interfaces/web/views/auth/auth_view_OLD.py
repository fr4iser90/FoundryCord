from fastapi import APIRouter, Request, Depends, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import templates_extension
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.web.infrastructure.config.env_loader import get_discord_oauth_config
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.infrastructure.constants import OWNER, ADMINS, MODERATORS, USERS
from app.shared.domain.auth.models import Role
from app.web.domain.auth.permissions import get_user_role
from app.shared.interface.logging.api import get_web_logger
import httpx

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_web_logger()
discord_config = get_discord_oauth_config()

class AuthView:
    """View für Authentifizierung über Discord OAuth"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/login")(self.login)
        self.router.get("/callback")(self.oauth_callback)
        self.router.get("/logout")(self.logout)
        self.router.get("/debug-session")(self.debug_session)
    
    def get_auth_service(self):
        """Dependency für den Auth-Service"""
        key_service = KeyManagementService()
        return WebAuthenticationService(key_service=key_service)
    
    async def login(self, request: Request):
        """Redirect to Discord OAuth directly"""
        if "user" in request.session:
            return RedirectResponse(url="/bot/overview")
            
        auth_url = (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={discord_config['client_id']}"
            f"&redirect_uri={discord_config['redirect_uri']}"
            f"&response_type=code"
            f"&scope=identify"
        )
        return RedirectResponse(url=auth_url)
    
    async def oauth_callback(self, code: str, request: Request):
        """Handle OAuth callback from Discord"""
        try:
            async with httpx.AsyncClient() as client:
                # Exchange code for token
                token_response = await client.post(
                    "https://discord.com/api/oauth2/token",
                    data={
                        "client_id": discord_config["client_id"],
                        "client_secret": discord_config["client_secret"],
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": discord_config["redirect_uri"],
                    }
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
                
                request.session["user"] = user
                request.session["token"] = token
                
                logger.info(f"User {user['username']} logged in successfully with role {user_role}")
                
                # Redirect based on role
                return RedirectResponse(
                    url="/home" if user_role == "OWNER" else "/dashboard",
                    status_code=status.HTTP_303_SEE_OTHER
                )
                
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
    async def logout(self, request: Request):
        """Clear session and redirect to home"""
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    async def debug_session(self, request: Request):
        """Debug endpoint to see session contents"""
        if not request.session.get("user", {}).get("role") == "OWNER":
            raise HTTPException(status_code=403, detail="Only OWNER can access debug information")
            
        return {
            "session": request.session,
            "user": request.session.get("user", "No user in session"),
            "token": "Present" if "token" in request.session else "Not present"
        }

# View-Instanz erzeugen
auth_view = AuthView()
login = auth_view.login
oauth_callback = auth_view.oauth_callback
logout = auth_view.logout
debug_session = auth_view.debug_session 