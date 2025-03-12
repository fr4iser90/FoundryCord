#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Complete Configuration
# =======================================================

# Prevent multiple inclusion
if [ -n "$CONFIG_LOADED" ]; then
    return 0
fi
export CONFIG_LOADED=1

# ------------------------------------------------------
# Server Configuration
# ------------------------------------------------------
export SERVER_USER="${SERVER_USER:-docker}"
export SERVER_HOST="${SERVER_HOST:-192.168.178.33}"
export SERVER_PORT="${SERVER_PORT:-22}"
export SERVER_KEY="${SERVER_KEY:-$HOME/.ssh/id_rsa}"

# ------------------------------------------------------
# Project Paths - COMPLETE CONFIGURATION
# ------------------------------------------------------
export LOCAL_GIT_DIR="$HOME/Documents/Git/NCC-DiscordBot"
export PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"

# Bot paths
export BOT_DOCKER_DIR="${PROJECT_ROOT_DIR}/docker/bot"
export BOT_DIR="${PROJECT_ROOT_DIR}/app/bot"

# Web paths
export WEB_DOCKER_DIR="${PROJECT_ROOT_DIR}/docker/web"
export WEB_DIR="${PROJECT_ROOT_DIR}/app/web"

# Database paths
export POSTGRES_DIR="${PROJECT_ROOT_DIR}/app/postgres"

# Local paths
export LOCAL_RESULTS_DIR="./test-results"
export LOCAL_TESTS_DIR="./tests"

# ------------------------------------------------------
# Docker Container Names
# ------------------------------------------------------
# Bot containers
export BOT_CONTAINER="homelab-discord-bot"
export POSTGRES_CONTAINER="homelab-postgres"
export REDIS_CONTAINER="homelab-redis"

# Web containers
export WEB_CONTAINER="homelab-web"
export WEB_DB_CONTAINER="homelab-web-db"
export WEB_CACHE_CONTAINER="homelab-web-cache"

# ------------------------------------------------------
# Docker Base Commands
# ------------------------------------------------------
export DOCKER_CMD="docker"
export DOCKER_COMPOSE_CMD="docker compose"

# ------------------------------------------------------
# Bot Docker Compose Commands
# ------------------------------------------------------
export BOT_COMPOSE_UP="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml up -d"
export BOT_COMPOSE_DOWN="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml down"
export BOT_COMPOSE_DOWN_VOLUMES="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml down -v"
export BOT_COMPOSE_BUILD="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml build"
export BOT_COMPOSE_BUILD_NOCACHE="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml build --no-cache"
export BOT_COMPOSE_LOGS="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml logs"
export BOT_COMPOSE_PS="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml ps"
export BOT_COMPOSE_RESTART="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml restart"

# ------------------------------------------------------
# Web Docker Compose Commands
# ------------------------------------------------------
export WEB_COMPOSE_UP="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml up -d web"
export WEB_COMPOSE_DOWN="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml stop web"
export WEB_COMPOSE_BUILD="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml build web"
export WEB_COMPOSE_BUILD_NOCACHE="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml build --no-cache web"
export WEB_COMPOSE_LOGS="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml logs web"
export WEB_COMPOSE_RESTART="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml restart web"

# ------------------------------------------------------
# Docker Container Commands
# ------------------------------------------------------
# Bot commands
export BOT_EXEC="${DOCKER_CMD} exec ${BOT_CONTAINER}"
export BOT_LOGS="${DOCKER_CMD} logs ${BOT_CONTAINER}"
export POSTGRES_EXEC="${DOCKER_CMD} exec ${POSTGRES_CONTAINER}"
export REDIS_EXEC="${DOCKER_CMD} exec ${REDIS_CONTAINER}"

# Web commands
export WEB_EXEC="${DOCKER_CMD} exec ${WEB_CONTAINER}"
export WEB_LOGS="${DOCKER_CMD} logs ${WEB_CONTAINER}"
export WEB_DB_EXEC="${DOCKER_CMD} exec ${WEB_DB_CONTAINER}"

# System commands
export DOCKER_STATS="${DOCKER_CMD} stats --no-stream"
export DOCKER_PRUNE="${DOCKER_CMD} system prune -f"
export DOCKER_VOLUME_PRUNE="${DOCKER_CMD} volume prune -f"

# ------------------------------------------------------
# Docker Compose File Paths
# ------------------------------------------------------
export BOT_COMPOSE_FILE="${PROJECT_ROOT_DIR}/docker/docker-compose.yml"
export BOT_DOCKERFILE="${BOT_DOCKER_DIR}/Dockerfile"
export BOT_ENV_FILE="${BOT_DOCKER_DIR}/.env"
export BOT_ENV_DISCORD="${BOT_DOCKER_DIR}/.env.discordbot"
export BOT_ENV_POSTGRES="${BOT_DOCKER_DIR}/.env.postgres"

export WEB_COMPOSE_FILE="${PROJECT_ROOT_DIR}/docker/docker-compose.yml"
export WEB_DOCKERFILE="${WEB_DOCKER_DIR}/Dockerfile.web"
export WEB_ENV_FILE="${WEB_DOCKER_DIR}/.env"

# ------------------------------------------------------
# Docker Runtime Options
# ------------------------------------------------------
export DOCKER_RESTART_POLICY="unless-stopped"
export DOCKER_MEMORY_LIMIT="512m"
export DOCKER_CPU_LIMIT="0.5"

# ------------------------------------------------------
# Colors for Terminal Output
# ------------------------------------------------------
export GREEN='\033[0;32m'
export RED='\033[0;31m'
export YELLOW='\033[0;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export WHITE='\033[0;37m'
export NC='\033[0m' # No Color

# ------------------------------------------------------
# Default Settings
# ------------------------------------------------------
export AUTO_RESTART="true"
export REBUILD_ON_DEPLOY="true"
export TEST_TIMEOUT="300"
export WAIT_TIMEOUT="60"
export DEBUG="true"
export VERBOSE_LOGS="true"

# ------------------------------------------------------
# Database Backup/Restore Commands
# ------------------------------------------------------
export DB_BACKUP_CMD="${POSTGRES_EXEC} pg_dump -U postgres -d homelab > backup_\$(date +%Y%m%d_%H%M%S).sql"
export DB_RESTORE_CMD="${POSTGRES_EXEC} psql -U postgres -d homelab < "
export DB_BACKUP_DIR="${PROJECT_ROOT_DIR}/backups"

# ------------------------------------------------------
# Application Commands
# ------------------------------------------------------
export BOT_PYTEST="${BOT_EXEC} pytest"
export BOT_ALEMBIC="${BOT_EXEC} alembic -c infrastructure/database/migrations/alembic.ini"
export BOT_PYTHON="${BOT_EXEC} python"

# ------------------------------------------------------
# Load local overrides if they exist
# ------------------------------------------------------
if [ -f "./utils/config/local_config.sh" ]; then
    source "./utils/config/local_config.sh"
    echo "Loaded local configuration overrides"
fi

# Print confirmation
echo "Configuration loaded successfully with bot and web components" 