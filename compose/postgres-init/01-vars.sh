#!/bin/bash
# Standardvariablen - übernehmen aus Umgebung oder Fallback
export DB_NAME="${POSTGRES_DB:-homelab}"
export APP_USER="${APP_DB_USER:-homelab_discord_bot}" 
export APP_PASSWORD="${APP_DB_PASSWORD:-$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)}"

# Für Abwärtskompatibilität
export PG_DEFAULT_DB="$DB_NAME"
export PG_DEFAULT_USER="$APP_USER"
export PG_DEFAULT_PASSWORD="$APP_PASSWORD"

echo "DB-Initialisierung: DB_NAME=$DB_NAME, APP_USER=$APP_USER"