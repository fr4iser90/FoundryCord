#!/bin/bash
set -e

# Datenbankparameter für Bot-Container
generate_db_params() {
  echo "Generiere Datenbankparameter..."
  
  # Grundparameter
  export POSTGRES_HOST="${POSTGRES_HOST:-homelab-postgres}"
  export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
  export POSTGRES_USER="${POSTGRES_USER:-postgres}"
  export POSTGRES_DB="${POSTGRES_DB:-homelab}"
  export APP_DB_USER="${APP_DB_USER:-homelab_discord_bot}"
  
  # Passwort aus geteiltem Volume laden, falls vorhanden
  if [ -f "/app/bot/database/credentials/db_credentials" ]; then
    source /app/bot/database/credentials/db_credentials
    echo "DB-Anmeldedaten aus Volume geladen"
  elif [ -z "$APP_DB_PASSWORD" ]; then
    # Fallback wenn keine Anmeldedaten gefunden
    export APP_DB_PASSWORD="homelab_password"
    echo "WARNUNG: Verwende Standard-Passwort"
  fi
  
  # Für SQLAlchemy-Verbindungsstring
  export DATABASE_URL="postgresql://${APP_DB_USER}:${APP_DB_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
  
  echo "DB-Konfiguration: ${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB} mit User ${APP_DB_USER}"
}

# Ausführen
generate_db_params
