#!/run/current-system/sw/bin/bash

# Variables
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
WATCH_CONSOLE=true
PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
DOCKER_DIR="${PROJECT_ROOT_DIR}/compose"

# Define what type of update this is
read -p "Do you want to perform a full update with rebuild? (y/n): " full_update

if [ "$full_update" == "y" ]; then
    # Full update with rebuild
    echo "Performing full update with rebuild..."
    
    # Stop containers
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose down"
    
    # Copy all files
    scp -r ~/Documents/Git/NCC-DiscordBot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    scp ~/Documents/Git/NCC-DiscordBot/compose/.env.discordbot ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    scp ~/Documents/Git/NCC-DiscordBot/compose/.env.postgres ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    
    # Rebuild and restart
    if [ "$WATCH_CONSOLE" = true ]; then
        ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose build --no-cache && docker-compose up"
    else
        ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose build && docker-compose up -d"
    fi
else
    # Code-only update: copy files and restart without rebuilding
    echo "Performing code-only update (ENVIRONMENT=development needed in .env.discordbot)..."
    
    # Copy Python files only
    scp -r ~/Documents/Git/NCC-DiscordBot/app/bot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/bot/
    
    # Restart the container without rebuilding
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose restart bot"
fi

echo "Update completed successfully!"