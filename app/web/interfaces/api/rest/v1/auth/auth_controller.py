from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.web.infrastructure.security.auth import get_current_user
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth", tags=["Authentication API"])

class AuthController:
    """Controller for pure API endpoints"""
    
    def __init__(self):
        self.router = router
        self.key_service = KeyManagementService()
        self.auth_service = WebAuthenticationService(self.key_service)
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        self.router.get("/me")(self.get_current_user_info)
        self.router.post("/logout")(self.logout)
    
    async def get_current_user_info(self, user=Depends(get_current_user)):
        """Get current user information"""
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        return {
            "id": user["id"],
            "username": user["username"],
            "avatar": user.get("avatar"),
            "role": user.get("role"),
            "authenticated": True
        }
    
    async def logout(self, request: Request):
        """Handle API logout"""
        request.session.clear()
        return {"status": "success"}

# Create controller instance
auth_controller = AuthController()
get_current_user_info = auth_controller.get_current_user_info
logout = auth_controller.logout 
