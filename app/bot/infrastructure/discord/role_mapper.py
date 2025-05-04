from typing import Optional, List
from app.shared.domain.auth.models.roles import Role, GUILD_ROLES

# Discord-specific role mapping
DISCORD_ROLE_MAPPING = {
    "OWNER": ["Bot Owner"],
    "ADMIN": ["Admin"],
    "MODERATOR": ["Moderator"],
    "USER": ["User"],
    "GUEST": ["Guest"]
}

class DiscordRoleMapper:
    @staticmethod
    def get_discord_roles(role: Role) -> List[str]:
        """Get Discord role names for a domain role"""
        return GUILD_ROLES.get(role.value, [])
    
    @staticmethod
    def from_discord_role(role_name: str) -> Optional[Role]:
        """Map a Discord role name to a domain Role"""
        for role_key, discord_roles in GUILD_ROLES.items():
            if role_name in discord_roles:
                return Role(role_key)
        return None