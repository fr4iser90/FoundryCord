#!/usr/bin/env bash

# =======================================================
# Unified Docker Application Configuration
# =======================================================

# Prevent multiple inclusion
if [ -n "$CONFIG_LOADED" ]; then
    return 0
fi
export CONFIG_LOADED=1

# ------------------------------------------------------
# Core Configuration Loading
# ------------------------------------------------------

# Load Local Configuration First
if [ -f "./utils/config/local_config.sh" ]; then
    source "./utils/config/local_config.sh"
elif [ -f "$(dirname "$0")/local_config.sh" ]; then
    source "$(dirname "$0")/local_config.sh"
fi

# ------------------------------------------------------
# Default Settings & Overrides
# ------------------------------------------------------

# Runtime mode
export RUN_LOCALLY="${RUN_LOCALLY:-false}"

# Project source directory (where the git repo is)
export SOURCE_DIR="$(pwd)"

# Determine effective project directory based on mode
if [ "$RUN_LOCALLY" = true ]; then
    export EFFECTIVE_PROJECT_DIR="${LOCAL_PROJECT_DIR}"
else
    export EFFECTIVE_PROJECT_DIR="${SERVER_PROJECT_DIR}"
fi

# ------------------------------------------------------
# Effective Path Configuration
# ------------------------------------------------------

# Set effective paths based on deployment mode
export EFFECTIVE_DOCKER_DIR="${EFFECTIVE_PROJECT_DIR}/docker"
export EFFECTIVE_APP_DIR="${EFFECTIVE_PROJECT_DIR}/app"
export EFFECTIVE_CONFIG_DIR="${EFFECTIVE_PROJECT_DIR}/utils/config"
export EFFECTIVE_SCRIPTS_DIR="${EFFECTIVE_PROJECT_DIR}/utils/scripts"

# ------------------------------------------------------
# Docker Configuration
# ------------------------------------------------------

# Container Management
export CONTAINER_NAMES="${CONTAINER_NAMES:-$PROJECT_NAME}"
export CONTAINER_LIST=(${CONTAINER_NAMES//,/ })
export MAIN_CONTAINER="${MAIN_CONTAINER:-${PROJECT_NAME}}"

# Docker Commands
export DOCKER_CMD="docker"
export DOCKER_COMPOSE_CMD="docker compose"

# Compose File Configuration
export COMPOSE_FILE="${EFFECTIVE_DOCKER_DIR}/docker-compose.yml"
export ENV_FILE="${EFFECTIVE_DOCKER_DIR}/.env"

# Basic Docker Compose Commands
export COMPOSE_UP="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} up"
export COMPOSE_DOWN="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} down"
export COMPOSE_BUILD="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} build"
export COMPOSE_LOGS="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} logs"
export COMPOSE_PS="${DOCKER_COMPOSE_CMD} -f ${COMPOSE_FILE} ps"

# ------------------------------------------------------
# Auto-start Configuration
# ------------------------------------------------------

export AUTO_START="${AUTO_START:-true}"
export AUTO_START_SERVICES="${AUTO_START_SERVICES:-all}"
export AUTO_START_WAIT="${AUTO_START_WAIT:-10}"
export AUTO_BUILD_ENABLED="${AUTO_BUILD_ENABLED:-true}"
export AUTO_START_FEEDBACK="${AUTO_START_FEEDBACK:-minimal}"

# Load auto-start config if exists
if [ -f "${EFFECTIVE_CONFIG_DIR}/auto_start.conf" ]; then
    source "${EFFECTIVE_CONFIG_DIR}/auto_start.conf"
fi

# ------------------------------------------------------
# Directory Creation
# ------------------------------------------------------

if [ "$RUN_LOCALLY" = true ]; then
    echo -e "\033[0;34mRunning in local mode with project directory: $LOCAL_PROJECT_DIR\033[0m"
    
    # Create local development directory structure
    mkdir -p "$LOCAL_PROJECT_DIR" \
             "$LOCAL_DOCKER_DIR" \
             "$LOCAL_APP_DIR"
fi

# ------------------------------------------------------
# Configuration Complete
# ------------------------------------------------------

echo -e "\033[0;32mConfiguration loaded successfully for project: ${PROJECT_NAME}\033[0m"
echo -e "\033[0;33mEnvironment: ${ENVIRONMENT}\033[0m"
if [ "$RUN_LOCALLY" = true ]; then
    echo -e "\033[0;34mDeploying to: ${LOCAL_PROJECT_DIR}\033[0m"
else
    echo -e "\033[0;34mDeploying to: ${SERVER_PROJECT_DIR}\033[0m"
fi 