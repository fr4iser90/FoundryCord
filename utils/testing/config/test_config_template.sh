#!/run/current-system/sw/bin/bash

# Configuration for remote testing
# Copy this file to test_config_local.sh and customize it with your settings
# The test.sh script will load test_config_local.sh if it exists

# Remote server settings
REMOTE_HOST="fr4iser.com"
REMOTE_USER="ubuntu"
REMOTE_KEY="$HOME/.ssh/id_rsa"
REMOTE_PORT=22
REMOTE_PROJECT_PATH="/docker/companion-management/homelab-discord-bot"

# Local settings
LOCAL_RESULTS_DIR="./test-results" 