from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
logger = get_bot_logger()

def is_bot_owner(user: AppUserEntity) -> bool:
    """Check if the user is a Bot owner."""
    return user.is_owner

def is_admin(user: AppUserEntity) -> bool:
    """Check if the user is an Admin or Super Admin."""
    if user.is_owner:
        return True
    return any(guild_user.role.name == "ADMIN" for guild_user in user.guild_roles)

def is_moderator(user: AppUserEntity) -> bool:
    """Check if the user is a Moderator or higher."""
    if is_admin(user):
        return True
    return any(guild_user.role.name == "MODERATOR" for guild_user in user.guild_roles)

def is_user(user: AppUserEntity) -> bool:
    """Check if the user is a regular User or higher."""
    if is_moderator(user):
        return True
    return any(guild_user.role.name == "USER" for guild_user in user.guild_roles)

def is_guest(user: AppUserEntity) -> bool:
    """Check if the user is a Guest or higher."""
    if user.is_owner:
        return True
    return bool(user.guild_roles)  # Any role counts as at least guest

def is_authorized(user: AppUserEntity) -> bool:
    """Check if the user is authorized."""
    # Use debug level for role checks
    logger.debug(f"Authorization check for user ID: {user.id}")
    
    # Check roles
    roles = {
        'owner': user.is_owner,
        'admin': is_admin(user),
        'moderator': is_moderator(user),
        'user': is_user(user),
        'guest': is_guest(user)
    }
    logger.debug(f"User roles: {roles}")
    
    return any(roles.values())
