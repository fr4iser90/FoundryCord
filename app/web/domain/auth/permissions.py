from fastapi import HTTPException, status
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    OWNER, ADMINS, MODERATORS, USERS, GUESTS
)

async def get_user_role(user_id: str) -> Role:
    """
    Determine a user's role based on their Discord ID
    """
    if str(user_id) in OWNER.values():
        return Role.SUPER_ADMIN
    elif str(user_id) in ADMINS.values():
        return Role.ADMIN
    elif str(user_id) in MODERATORS.values():
        return Role.MODERATOR
    elif str(user_id) in USERS.values():
        return Role.USER
    else:
        return Role.GUEST

async def require_role(user: dict, required_role: Role = Role.MODERATOR):
    """
    Verify that a user has at least the required role
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_id = user.get("id")
    user_role = await get_user_role(user_id)
    
    if not user_role.can_access(required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: requires {required_role.value} role or higher"
        )
    
    # Add the role to the user object for later use
    user["role"] = user_role.value
    return user 