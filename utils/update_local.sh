#!/run/current-system/sw/bin/bash


# Setze das Zielverzeichnis und Serverinformationen
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
DOCKER_DIR="/home/docker/docker/companion-management/homelab-discord-bot/compose"

# 1. Stoppe den Docker-Container
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${DOCKER_DIR}/docker-compose.yml down"

# 2. Kopiere die neuen Dateien auf den Server
scp -r ~/Documents/Git/NCC-DiscordBot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
scp ~/Documents/Git/NCC-DiscordBot/compose/.env.discordbot ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
scp ~/Documents/Git/NCC-DiscordBot/compose/.env.postgres ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}

# 3. Starte den Docker-Container neu
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${DOCKER_DIR}/docker-compose.yml build"
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose -f ${DOCKER_DIR}/docker-compose.yml up"

echo "Update abgeschlossen und Container neu gestartet!"
