from fastapi import APIRouter, Depends, HTTPException, status
from app.web.infrastructure.security.auth import get_current_user, User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.get("/me", response_model=User)
async def get_current_user_info(user = Depends(get_current_user)):
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

@router.get("/logout")
async def logout():
    """Returns instruction for client-side logout"""
    return {
        "message": "To logout, delete the access_token cookie"
    }
