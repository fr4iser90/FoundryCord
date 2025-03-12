#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Centralized Configuration
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
# Project Paths
# ------------------------------------------------------
export PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
export DOCKER_DIR="${PROJECT_ROOT_DIR}/compose"
export BOT_DIR="${PROJECT_ROOT_DIR}/app/bot"
export LOCAL_RESULTS_DIR="./test-results"
export LOCAL_TESTS_DIR="./tests"

# ------------------------------------------------------
# Docker Container Names
# ------------------------------------------------------
export BOT_CONTAINER="homelab-discord-bot"
export POSTGRES_CONTAINER="homelab-postgres"
export REDIS_CONTAINER="homelab-redis"

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
# Test Configuration
# ------------------------------------------------------
export RUN_SYSTEM_TESTS="${RUN_SYSTEM_TESTS:-true}"
export RUN_UNIT_TESTS="${RUN_UNIT_TESTS:-true}"
export RUN_INTEGRATION_TESTS="${RUN_INTEGRATION_TESTS:-true}"
export TEST_TIMEOUT="${TEST_TIMEOUT:-300}"

# ------------------------------------------------------
# Deployment Configuration
# ------------------------------------------------------
export AUTO_RESTART="${AUTO_RESTART:-true}"
export WAIT_TIMEOUT="${WAIT_TIMEOUT:-60}"
export REBUILD_ON_DEPLOY="${REBUILD_ON_DEPLOY:-true}"

# ------------------------------------------------------
# Load environment-specific config if exists
# ------------------------------------------------------
ENV_CONFIG_FILE="./utils/config/env_${ENVIRONMENT:-dev}.sh"
if [ -f "$ENV_CONFIG_FILE" ]; then
    source "$ENV_CONFIG_FILE"
    echo "Loaded environment config: $ENV_CONFIG_FILE"
fi

# ------------------------------------------------------
# Load local overrides if they exist
# ------------------------------------------------------
if [ -f "./utils/config/local_config.sh" ]; then
    source "./utils/config/local_config.sh"
    echo "Loaded local configuration overrides"
fi

echo "Configuration loaded successfully" 