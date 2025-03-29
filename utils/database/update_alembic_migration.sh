#!/bin/bash
# update_alembic_migration.sh - Automatisiert Alembic-Migrationen ohne manuelle Kommandos

set -e

# Variablen aus config.sh importieren
source "$(dirname "$0")/../config/config.sh"

echo "=== Homelab Discord Bot: Alembic Migration Tool ==="

# Use a more reliable way to check if running on the server
if [ "$1" != "--on-server" ]; then
    echo "Kopiere aktuelle Codebase zum Server..."
    scp -r ~/Documents/Git/NCC-DiscordBot/app/bot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/bot/
    scp -r ~/Documents/Git/NCC-DiscordBot/utils/update_alembic_migration.sh ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/utils/
    
    echo "Führe Migration auf dem Server aus..."
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${PROJECT_ROOT_DIR} && bash utils/update_alembic_migration.sh --on-server"
    exit $?
fi

# Ab hier läuft das Skript auf dem Server
echo "Führe Alembic-Migration im Container aus..."
CONTAINER_ID=$(docker ps -qf "name=discord-server-bot")

if [ -z "$CONTAINER_ID" ]; then
    echo "Fehler: Discord Bot Container nicht gefunden!"
    exit 1
fi

# Apply existing migrations first
docker exec "$CONTAINER_ID" bash -c "export USE_ALEMBIC=true && alembic -c infrastructure/database/migrations/alembic.ini upgrade head"

# Now create a new migration
docker exec "$CONTAINER_ID" bash -c "export USE_ALEMBIC=true && alembic -c infrastructure/database/migrations/alembic.ini revision --autogenerate -m 'Add category_type to category_mappings'"

# Apply the new migration
docker exec "$CONTAINER_ID" bash -c "export USE_ALEMBIC=true && alembic -c infrastructure/database/migrations/alembic.ini upgrade head"

echo "Migration abgeschlossen. Container wird neu gestartet..."
cd ${DOCKER_DIR} && docker compose restart bot
echo "=== Alembic-Migration erfolgreich durchgeführt ==="