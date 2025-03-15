# app/bot/domain/auth/models/__init__.py
from .user import User
from .permission import Permission
from .role import Role

# Erst nach den Klassen die Konstanten importieren
from .role import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS, SERVER_ROLES

__all__ = [
    'User',
    'Role', 'SERVER_ROLES',
    'Permission',
    'SUPER_ADMINS', 'ADMINS', 'MODERATORS', 'USERS', 'GUESTS'
]