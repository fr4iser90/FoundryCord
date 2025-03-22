from fastapi import HTTPException, status
from enum import Enum
from app.shared.infrastructure.constants import (
    OWNER, ADMINS, MODERATORS, USERS, GUESTS
)

# Define the Role enum - only once!
class Role(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"
    GUEST = "GUEST"

def get_user_role_from_id(user_id: str) -> Role:
    """
    Determine a user's role based on their Discord ID
    """
    if str(user_id) in OWNER.values():
        return Role.OWNER
    elif str(user_id) in ADMINS.values():
        return Role.ADMIN
    elif str(user_id) in MODERATORS.values():
        return Role.MODERATOR
    elif str(user_id) in USERS.values():
        return Role.USER
    else:
        return Role.GUEST

def get_user_role(user) -> Role:
    """Get role from user object or existing role string"""
    # Check if user is None
    if not user:
        return Role.GUEST
        
    # 1. If user has an 'id' field and no explicit role, determine from ID
    if 'id' in user and ('role' not in user or not user['role']):
        return get_user_role_from_id(user['id'])
    
    # 2. If the role is already in the user object, use that
    role_str = user.get("role", "GUEST")
    
    # Convert string to enum
    try:
        return Role(role_str)
    except ValueError:
        return Role.GUEST

async def require_role(user, required_role: Role):
    """Check if user has required role or higher"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user role
    user_role = get_user_role(user)
    
    # Check if role is sufficient
    if not is_role_sufficient(user_role, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role.value}",
        )

def is_role_sufficient(user_role: Role, required_role: Role) -> bool:
    """Check if user_role is sufficient for required_role"""
    role_hierarchy = {
        Role.OWNER: 100,
        Role.ADMIN: 80,
        Role.MODERATOR: 60,
        Role.USER: 40,
        Role.GUEST: 20
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 100) 