#!/bin/bash
# Ein Skript, das den Code aktualisiert und dann die Datenbank migriert

# Variablen aus config.sh importieren
source "$(dirname "$0")/../config/config.sh"

echo "=== Homelab Discord Bot: Remote Update & Migration Tool ==="

# 1. Code auf den Server kopieren
echo "Kopiere den aktuellen Code zum Server..."
scp -r ~/Documents/Git/NCC-DiscordBot/app/bot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/bot/
scp -r ~/Documents/Git/NCC-DiscordBot/utils/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/utils/database/

# 2. Führe das Datenbank-Update auf dem Server aus
echo "Führe Datenbank-Update auf dem Server aus..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${PROJECT_ROOT_DIR} && bash utils/database/category_v002.sh"

# 3. Container neu starten
echo "Starte Bot-Container neu..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose restart bot"

echo "Update und Datenbank-Migration erfolgreich abgeschlossen!"