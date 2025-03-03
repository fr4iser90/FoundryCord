# config/users.py
import os

# Umgebungsvariablen auslesen
super_admins_env = os.getenv('SUPER_ADMINS', '')  # Super Admins
admins_env = os.getenv('ADMINS', '')  # Admins
guests_env = os.getenv('GUESTS', '')  # Guests
moderators_env = os.getenv('MODERATORS', '')  # Moderators
users_env = os.getenv('USERS', '')  # Regular Users
devs_env = os.getenv('DEVS', '')  # Developers

# Funktion zum Umwandeln der Umgebungsvariablen in ein Dictionary
def parse_users(users_str):
    users_dict = {}
    if users_str:
        for user_entry in users_str.split(','):
            if '|' in user_entry:
                username, user_id = user_entry.split('|')
                users_dict[username.strip()] = user_id.strip()
    return users_dict

# Erstelle die Dictionaries für alle Rollen
SUPER_ADMINS = parse_users(super_admins_env)
ADMINS = parse_users(admins_env)
GUESTS = parse_users(guests_env)
MODERATORS = parse_users(moderators_env)
USERS = parse_users(users_env)
DEVS = parse_users(devs_env)

# Optional: Weitere Rollen können hier hinzugefügt werden
