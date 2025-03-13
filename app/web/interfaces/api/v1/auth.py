from fastapi import APIRouter, Depends, HTTPException, status
from app.web.domain.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class UserInfo(BaseModel):
    id: str
    username: str
    avatar: Optional[str] = None

@router.get("/me", response_model=UserInfo)
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
        "avatar": user.get("avatar")
    }

@router.get("/logout")
async def logout():
    """Returns instruction for client-side logout"""
    return {
        "message": "To logout, delete the access_token cookie"
    }
