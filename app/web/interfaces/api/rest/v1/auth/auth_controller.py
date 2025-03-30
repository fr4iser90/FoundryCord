from fastapi import APIRouter, Depends, HTTPException, status
from app.web.infrastructure.security.auth import get_current_user, User

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

class AuthController:
    """Controller für Authentifizierungs-Funktionen"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/me")(self.get_current_user_info)
        self.router.get("/logout")(self.logout)
    
    async def get_current_user_info(self, user = Depends(get_current_user)):
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
            "authenticated": True
        }
    
    async def logout(self):
        """Returns instruction for client-side logout"""
        return {
            "message": "To logout, delete the access_token cookie"
        }

# Für API-Kompatibilität
auth_controller = AuthController()
get_current_user_info = auth_controller.get_current_user_info
logout = auth_controller.logout 