#!/bin/bash
set -e

# Prüfung, ob eine manuelle Initialisierung erforderlich ist
if [ -d "/var/lib/postgresql/data/base" ]; then
  echo "Bestehende Datenbankdateien gefunden, prüfe ob Datenbank existiert..."
  
  # Prüfen, ob die Datenbank bereits existiert
  if ! psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "homelab"; then
    echo "Datenbank 'homelab' existiert nicht, erstelle sie..."
    psql -U postgres -c "CREATE DATABASE homelab;"
  fi
  
  # Prüfen, ob der Benutzer bereits existiert
  if ! psql -U postgres -c "\du" | grep -qw "homelab_discord_bot"; then
    echo "Benutzer 'homelab_discord_bot' existiert nicht, erstelle ihn..."
    # Verwende das Passwort aus der Umgebungsvariable oder generiere ein zufälliges
    export APP_PASSWORD="${APP_DB_PASSWORD:-$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)}"
    psql -U postgres -c "CREATE USER homelab_discord_bot WITH PASSWORD '${APP_PASSWORD}';"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE homelab TO homelab_discord_bot;"
    
    # Anmeldedaten speichern mit korrekten Berechtigungen
    mkdir -p /var/lib/postgresql/shared
    echo "APP_DB_USER=homelab_discord_bot" > /var/lib/postgresql/shared/db_credentials
    echo "APP_DB_PASSWORD=${APP_PASSWORD}" >> /var/lib/postgresql/shared/db_credentials
    chmod 644 /var/lib/postgresql/shared/db_credentials
  fi
fi