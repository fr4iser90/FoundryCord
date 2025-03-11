#!/run/current-system/sw/bin/bash

# Variablen
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
WATCH_CONSOLE=true
PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
DOCKER_DIR="${PROJECT_ROOT_DIR}/compose"
REMOVE_APP=false
REMOVE_VOLUMES=false
FULL_BUILD=false

# Argumente parsen
for arg in "$@"; do
    case $arg in
        --remove-old|--build-completely-new)
            REMOVE_APP=true
            shift
            ;;
        --full-build)
            FULL_BUILD=true
            shift
            ;;
        --remove-volumes)
            REMOVE_VOLUMES=true
            shift
            ;;      
        # Unbekannte Option
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

if [ "$REMOVE_VOLUMES" = true ]; then
    echo "Removing volumes..."
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker compose down -v"
fi

# Art des Updates definieren
if [ "$FULL_BUILD" = true ]; then
    full_update="y"
else
    read -p "Do you want to perform a full update with rebuild? (y/n): " full_update
fi

if [ "$full_update" == "y" ]; then
    echo "Performing full update with rebuild..."

    # Container stoppen
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose down"

    # App-Verzeichnis optional entfernen
    if [ "$REMOVE_APP" = true ]; then
        echo "Removing existing app directory..."
        ssh ${SERVER_USER}@${SERVER_HOST} "rm -rf ${PROJECT_ROOT_DIR}"
    fi

    # Dateien kopieren
    scp -r ~/Documents/Git/NCC-DiscordBot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    #scp ~/Documents/Git/NCC-DiscordBot/compose/.env.discordbot ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    #scp ~/Documents/Git/NCC-DiscordBot/compose/.env.postgres ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    scp ~/Documents/Git/NCC-DiscordBot/compose/.env ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}
    
    # Neu bauen und starten
    if [ "$WATCH_CONSOLE" = true ]; then
        ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose build --no-cache && docker-compose up"
    else
        ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose build && docker-compose up -d"
    fi
else
    echo "Performing code-only update (ENVIRONMENT=development needed in .env.discordbot)..."

    # Nur Python-Dateien kopieren
    scp -r ~/Documents/Git/NCC-DiscordBot/app/bot/* ${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/bot/

    # Container neustarten ohne Neuaufbau
    ssh ${SERVER_USER}@${SERVER_HOST} "cd ${DOCKER_DIR} && docker-compose restart bot"
fi

echo "Update completed successfully!"
