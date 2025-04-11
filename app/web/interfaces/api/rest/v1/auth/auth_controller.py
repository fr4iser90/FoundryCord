from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class AuthController(BaseController):
    """Controller for authentication functionality"""
    
    def __init__(self):
        super().__init__(prefix="/auth", tags=["Authentication"])
        self._register_routes()

    def _register_routes(self):
        """Register all authentication routes"""
        self.router.post("/login")(self.login)
        self.router.post("/logout")(self.logout)
        self.router.get("/me")(self.get_current_user_info)
        self.router.post("/refresh")(self.refresh_token)
        self.router.get("/login")(self.login)
        self.router.get("/callback")(self.auth_callback)
        self.router.get("/logout")(self.logout)
        self.router.get("/me")(self.get_current_user_info)

    async def login(self, request: Request):
        """Redirects the user to Discord for authentication."""
        # Build the Discord authorization URL
        auth_url = await self.auth_service.get_authorization_url()
        return RedirectResponse(url=auth_url)

    async def auth_callback(self, request: Request, code: str):
        """Handles the callback from Discord after authentication."""
        try:
            # Exchange code for token and get user info
            user_info = await self.auth_service.handle_callback(code)
            
            # Store user info in session
            request.session["user"] = user_info
            self.logger.info(f"User {user_info.get('username')} logged in.")
            
            # Redirect to home page or intended destination
            return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
            
        except Exception as e:
            self.logger.error(f"Authentication callback failed: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authentication failed")

    async def get_current_user_info(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get current user information"""
        try:
            # Get user info through service
            user_info = await self.user_service.get_user_info(current_user.id)
            return self.success_response(user_info)
        except Exception as e:
            return self.handle_exception(e)

    async def logout(self, request: Request):
        """Logout endpoint"""
        user = request.session.get("user")
        if user:
            self.logger.info(f"User {user.get('username')} logged out.")
            request.session.clear()
        # Redirect to home page or login page
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    async def refresh_token(self, request: Request, refresh_token: str):
        """Refresh access token"""
        try:
            # Refresh token through service
            new_token = await self.auth_service.refresh_token(refresh_token)
            if not new_token:
                return self.error_response("Ungültiger Refresh Token", 401)
            
            return self.success_response({
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 3600
            })
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
auth_controller = AuthController() 
