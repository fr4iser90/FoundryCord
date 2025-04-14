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

# Database Configuration (Anpassen für FoundryCord falls nötig, sonst entfernen?)
# export DB_NAME="${PROJECT_NAME}_db" # Beispiel, anpassen!
# export DB_CONTAINER_NAME="${PROJECT_NAME}-db" # Beispiel, anpassen!
export DB_NAME="foundrycord_db"#!/usr/bin/env bash

# Server Configuration
export SERVER_USER="fr4iser"
export SERVER_HOST="192.168.178.36"
export SERVER_PORT="22"
export SERVER_KEY="$HOME/.ssh/id_rsa"

# Project Configuration
export PROJECT_NAME="yassist"
export ENVIRONMENT="development"

# Remote Server Paths
export SERVER_ROOT="/home/${SERVER_USER}/projects"
export SERVER_PROJECT_DIR="${SERVER_ROOT}/ai-stacks/yassist"

# Local Development Configuration
export LOCAL_GIT_DIR="$HOME/Documents/Git/yassist"

export LOCAL_DEV_ROOT="$HOME/Documents/Development"
export LOCAL_PROJECT_DIR="${LOCAL_DEV_ROOT}/yassist"
export LOCAL_DOCKER_DIR="${LOCAL_PROJECT_DIR}/docker"
export LOCAL_APP_DIR="${LOCAL_PROJECT_DIR}/app"

# Database Configuration (Added)
export DB_NAME="${PROJECT_NAME}_db"
export DB_CONTAINER_NAME="${PROJECT_NAME}-db"

# Container configuration (Placeholder names for the new stack)
export CONTAINER_NAMES="${PROJECT_NAME}-ollama,${PROJECT_NAME}-anythingllm,${PROJECT_NAME}-comfyui,${DB_CONTAINER_NAME},${PROJECT_NAME}-n8n" # Used DB_CONTAINER_NAME
export MAIN_CONTAINER="${PROJECT_NAME}-ollama" # Placeholder main container

# Project-specific settings
export AUTO_START="true"
export AUTO_BUILD_ENABLED="true"
export REBUILD_ON_DEPLOY="true"


# Saved from unified config on Mi 2. Apr 16:14:07 CEST 2025
export DB_CONTAINER_NAME="foundrycord-db"

# Container configuration
export CONTAINER_NAMES="foundrycord-bot,foundrycord-db,foundrycord-cache,foundrycord-web"
export MAIN_CONTAINER="foundrycord-bot"

# Development Hot-Reload Targets (Used by --hot-reload=TARGET)
# Define the names of components that can be hot-reloaded.
# Assumes source is LOCAL_GIT_DIR/<target> and destination is LOCAL_APP_DIR/<target>
export HOT_RELOAD_TARGETS="web bot shared" # Adjust as needed for FoundryCord

# Project-specific settings
export AUTO_START="true"
export AUTO_BUILD_ENABLED="true"
export REBUILD_ON_DEPLOY="true"

# Saved from unified config on $(date) # Datum aktualisieren
