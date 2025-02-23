# config/users.py
import os

# Umgebungsvariablen auslesen
admins_env = os.getenv('ADMINS', '')  # Standardwert ist ein leerer String
guests_env = os.getenv('GUESTS', '')

# Funktion zum Umwandeln der Umgebungsvariablen in ein Dictionary
def parse_users(users_str):
    users_dict = {}
    if users_str:
        for user_entry in users_str.split(','):
            if ':' in user_entry:
                username, user_id = user_entry.split(':')
                users_dict[username.strip()] = user_id.strip()
    return users_dict

# ADMINS und GUESTS dynamisch erstellen
ADMINS = parse_users(admins_env)
GUESTS = parse_users(guests_env)