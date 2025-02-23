#!/run/current-system/sw/bin/bash


# Setze das Zielverzeichnis und Serverinformationen
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
SERVER_DIR="/home/docker/docker/companion-management/homelab-discord-bot"

# 1. Stoppe den Docker-Container
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${SERVER_DIR}/docker-compose.yml down"

# 2. Kopiere die neuen Dateien auf den Server
scp -r ~/Documents/Git/homelab_bot/* ${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}
scp ~/Documents/Git/homelab_bot/.env ${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}

# 3. Starte den Docker-Container neu
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${SERVER_DIR}/docker-compose.yml build"
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${SERVER_DIR}/docker-compose.yml up"

echo "Update abgeschlossen und Container neu gestartet!"
