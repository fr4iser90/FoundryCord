import os

# Funktion zum Umwandeln der Umgebungsvariablen in ein Dictionary
def parse_users(users_str):
    users_dict = {}
    if users_str:
        for user_entry in users_str.split(','):
            if '|' in user_entry:
                username, user_id = user_entry.split('|')
                users_dict[username.strip()] = user_id.strip()
    return users_dict

# Lese Umgebungsvariablen aus (falls nicht gesetzt, wird ein leerer String verwendet)
super_admins_env = os.getenv('SUPER_ADMINS', '')
admins_env = os.getenv('ADMINS', '')
moderators_env = os.getenv('MODERATORS', '')
users_env = os.getenv('USERS', '')
guests_env = os.getenv('GUESTS', '')

# Erstelle die Dictionaries für alle Rollen
# Wenn die Umgebungsvariable leer ist, wird ein leeres Dictionary verwendet
SUPER_ADMINS = parse_users(super_admins_env) if super_admins_env else {}
ADMINS = parse_users(admins_env) if admins_env else {}
MODERATORS = parse_users(moderators_env) if moderators_env else {}
USERS = parse_users(users_env) if users_env else {}
GUESTS = parse_users(guests_env) if guests_env else {}

if not super_admins_env and not admins_env:
    print("Warning: Neither SUPER_ADMINS nor ADMINS environment variables are set. Both roles will be empty.")

