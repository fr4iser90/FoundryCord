# modules/auth/permissions.py
from config.users import ADMINS, GUESTS

def is_admin(user):
    """Prüft, ob der Benutzer ein Admin ist."""
    return str(user.id) in ADMINS.values()

def is_guest(user):
    """Prüft, ob der Benutzer ein Gast ist."""
    return str(user.id) in GUESTS.values()

def is_authorized(user):
    """Prüft, ob der Benutzer entweder Admin oder Gast ist."""
    return is_admin(user) or is_guest(user)