#!/usr/bin/env bash

# Server Configuration
export SERVER_USER="docker"
export SERVER_HOST="192.168.178.33"
export SERVER_PORT="22"
export SERVER_KEY="$HOME/.ssh/id_rsa"

# Project Configuration
export PROJECT_NAME="FoundryCord"
export ENVIRONMENT="development"

# Remote Server Paths
export SERVER_ROOT="/home/docker/docker"
export SERVER_PROJECT_DIR="${SERVER_ROOT}/companion-management/FoundryCord"

# Local Development Configuration
export LOCAL_GIT_DIR="$HOME/Documents/Git/${PROJECT_NAME}"

export LOCAL_DEV_ROOT="$HOME/Documents/Development"
export LOCAL_PROJECT_DIR="${LOCAL_DEV_ROOT}/FoundryCord"
export LOCAL_DOCKER_DIR="${LOCAL_PROJECT_DIR}/docker"
export LOCAL_APP_DIR="${LOCAL_PROJECT_DIR}/app"

# Container configuration
export CONTAINER_NAMES="foundrycord-bot,foundrycord-db,foundrycord-cache,foundrycord-web"
export MAIN_CONTAINER="foundrycord-bot"

# Project-specific settings
export AUTO_START="true"
export AUTO_BUILD_ENABLED="true"
export REBUILD_ON_DEPLOY="true"

# Saved from unified config on $(date)