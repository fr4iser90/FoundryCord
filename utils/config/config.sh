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
export DOCKER_DIR="${PROJECT_ROOT_DIR}/docker"
export APP_DIR="${PROJECT_ROOT_DIR}/app"
export BOT_DIR="${PROJECT_ROOT_DIR}/app/bot"
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
export BOT_COMPOSE_UP="${DOCKER_COMPOSE_CMD} -f ${PROJECT_ROOT_DIR}/docker/docker-compose.yml up"
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
export BOT_DOCKERFILE="${DOCKER_DIR}/Dockerfile.bot"
export ENV_FILE="${DOCKER_DIR}/.env"

export WEB_COMPOSE_FILE="${PROJECT_ROOT_DIR}/docker/docker-compose.yml"
export WEB_DOCKERFILE="${DOCKER_DIR}/Dockerfile.web"


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
# Auto-start Configuration
# ------------------------------------------------------
export AUTO_START="${AUTO_START:-true}"
export AUTO_START_SERVICES="${AUTO_START_SERVICES:-all}"
export AUTO_START_WAIT="${AUTO_START_WAIT:-10}"
export AUTO_BUILD_ENABLED="${AUTO_BUILD_ENABLED:-true}"
export AUTO_START_FEEDBACK="${AUTO_START_FEEDBACK:-minimal}"

# If auto-start config file exists, source it
if [ -f "${PROJECT_ROOT_DIR}/utils/config/auto_start.conf" ]; then
    source "${PROJECT_ROOT_DIR}/utils/config/auto_start.conf"
elif [ -f "./utils/config/auto_start.conf" ]; then
    source "./utils/config/auto_start.conf"
fi

# ------------------------------------------------------
# Ensure local config doesn't overwrite your settings
# ------------------------------------------------------
# We'll PRESERVE your settings by not loading local_config here
# but instead save your current settings TO local_config
# ------------------------------------------------------

# Save current settings if local_config doesn't exist
if [ ! -f "./utils/config/local_config.sh" ]; then
    mkdir -p "./utils/config"
    echo "#!/usr/bin/env bash" > "./utils/config/local_config.sh"
    echo "" >> "./utils/config/local_config.sh"
    echo "# Local configuration - AUTOMATICALLY GENERATED" >> "./utils/config/local_config.sh"
    echo "export SERVER_USER=\"${SERVER_USER}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_HOST=\"${SERVER_HOST}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_PORT=\"${SERVER_PORT}\"" >> "./utils/config/local_config.sh"
    echo "export PROJECT_ROOT_DIR=\"${PROJECT_ROOT_DIR}\"" >> "./utils/config/local_config.sh"
    echo "export ENVIRONMENT=\"${ENVIRONMENT}\"" >> "./utils/config/local_config.sh"
    echo "# Saved from your config.sh on $(date)" >> "./utils/config/local_config.sh"
fi

# Print confirmation
echo "Configuration loaded successfully with bot and web components"

# ------------------------------------------------------
# Local Mode Configuration
# ------------------------------------------------------
# These variables are used when RUN_LOCALLY=true

# If not defined in local_config.sh, set defaults
export LOCAL_PROJECT_DIR="${LOCAL_PROJECT_DIR:-$HOME/Documents/Development/NCC-DiscordBot}"
export LOCAL_DOCKER_DIR="${LOCAL_DOCKER_DIR:-$LOCAL_PROJECT_DIR/docker}"
export LOCAL_APP_DIR="${LOCAL_APP_DIR:-$LOCAL_PROJECT_DIR/app}"
export LOCAL_BOT_DIR="${LOCAL_BOT_DIR:-$LOCAL_PROJECT_DIR/app/bot}"
export LOCAL_WEB_DIR="${LOCAL_WEB_DIR:-$LOCAL_PROJECT_DIR/app/web}"

# Create directories if they don't exist when in local mode
if [ "$RUN_LOCALLY" = true ]; then
    echo "Running in local mode with project directory: $LOCAL_PROJECT_DIR"
    mkdir -p "$LOCAL_PROJECT_DIR" "$LOCAL_DOCKER_DIR" "$LOCAL_APP_DIR" "$LOCAL_BOT_DIR" "$LOCAL_WEB_DIR"
    
    # Use local paths instead of remote paths when in local mode
    EFFECTIVE_DOCKER_DIR="$LOCAL_DOCKER_DIR"
    EFFECTIVE_APP_DIR="$LOCAL_APP_DIR"
    EFFECTIVE_BOT_DIR="$LOCAL_BOT_DIR"
    EFFECTIVE_WEB_DIR="$LOCAL_WEB_DIR"
else
    # Use remote paths
    EFFECTIVE_DOCKER_DIR="$DOCKER_DIR"
    EFFECTIVE_APP_DIR="$APP_DIR"
    EFFECTIVE_BOT_DIR="$BOT_DIR"
    EFFECTIVE_WEB_DIR="$WEB_DIR"
fi

export EFFECTIVE_DOCKER_DIR EFFECTIVE_APP_DIR EFFECTIVE_BOT_DIR EFFECTIVE_WEB_DIR 