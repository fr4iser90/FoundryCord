#!/usr/bin/env bash

# =======================================================
# Unified Docker Application Configuration
# =======================================================

# Prevent multiple inclusion
if [ -n "$CONFIG_LOADED" ]; then
    return 0
fi
export CONFIG_LOADED=1

# Load Local Configuration First
if [ -f "./utils/config/local_config.sh" ]; then
    source "./utils/config/local_config.sh"
elif [ -f "$(dirname "$0")/local_config.sh" ]; then
    source "$(dirname "$0")/local_config.sh"
fi

# Local mode settings
export RUN_LOCALLY="${RUN_LOCALLY:-false}"

# Server Configuration
export SERVER_USER="${SERVER_USER}"
export SERVER_HOST="${SERVER_HOST}"
export SERVER_PORT="${SERVER_PORT}"
export SERVER_KEY="${SERVER_KEY:-$HOME/.ssh/id_rsa}"

# Project Configuration
export PROJECT_ROOT_DIR="${PROJECT_ROOT_DIR}"
export PROJECT_NAME="${PROJECT_NAME}"

# Docker Paths
export DOCKER_DIR="${PROJECT_ROOT_DIR}/docker"
export APP_DIR="${PROJECT_ROOT_DIR}/app"

# Local Paths
export LOCAL_RESULTS_DIR="./test-results"
export LOCAL_TESTS_DIR="./tests"

# Docker Container Names
export CONTAINER_NAMES="${CONTAINER_NAMES}"
export CONTAINER_LIST=(${CONTAINER_NAMES//,/ })

# Docker Base Commands
export DOCKER_CMD="docker"
export DOCKER_COMPOSE_CMD="docker compose"

# Docker Compose Commands
export COMPOSE_FILE="${PROJECT_ROOT_DIR}/docker/docker-compose.yml"
export ENV_FILE="${PROJECT_ROOT_DIR}/docker/.env"
export COMPOSE_UP="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} up"
export COMPOSE_DOWN="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} down"

# Auto-start Configuration
export AUTO_START="${AUTO_START:-true}"
export AUTO_START_SERVICES="${AUTO_START_SERVICES:-all}"
export AUTO_START_WAIT="${AUTO_START_WAIT:-10}"
export AUTO_BUILD_ENABLED="${AUTO_BUILD_ENABLED:-true}"
export AUTO_START_FEEDBACK="${AUTO_START_FEEDBACK:-minimal}"

# Source auto-start config if it exists
if [ -f "${PROJECT_ROOT_DIR}/utils/config/auto_start.conf" ]; then
    source "${PROJECT_ROOT_DIR}/utils/config/auto_start.conf"
elif [ -f "./utils/config/auto_start.conf" ]; then
    source "./utils/config/auto_start.conf"
fi

# Save current settings if local_config doesn't exist
if [ ! -f "./utils/config/local_config.sh" ]; then
    mkdir -p "./utils/config"
    {
        echo "#!/usr/bin/env bash"
        echo ""
        echo "# Local configuration - AUTOMATICALLY GENERATED"
        echo "export SERVER_USER=\"${SERVER_USER}\""
        echo "export SERVER_HOST=\"${SERVER_HOST}\""
        echo "export SERVER_PORT=\"${SERVER_PORT}\""
        echo "export PROJECT_ROOT_DIR=\"${PROJECT_ROOT_DIR}\""
        echo "export CONTAINER_NAMES=\"${CONTAINER_NAMES}\""
        echo "# Saved from your config.sh on $(date)"
    } > "./utils/config/local_config.sh"
fi

# Print confirmation
echo "Configuration loaded successfully for project: ${PROJECT_NAME}"

# Local Mode Configuration
if [ "$RUN_LOCALLY" = true ]; then
    echo "Running in local mode with project directory: $PROJECT_ROOT_DIR"
    mkdir -p "$PROJECT_ROOT_DIR" "$DOCKER_DIR" "$APP_DIR"
fi 