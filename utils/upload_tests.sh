#!/usr/bin/env bash

# Script to upload test files to the remote server

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Server configuration
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
REMOTE_DIR="/home/docker/docker/companion-management/homelab-discord-bot"

echo "Uploading test files to ${SERVER_HOST}..."

# Create test directory if it doesn't exist
ssh ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${REMOTE_DIR}/tests"

# Upload all test files
scp tests/test_*.py ${SERVER_USER}@${SERVER_HOST}:${REMOTE_DIR}/tests/

# Verify the test files were uploaded correctly
TEST_FILES=$(ssh ${SERVER_USER}@${SERVER_HOST} "ls ${REMOTE_DIR}/tests/test_*.py 2>/dev/null || echo 'No test files found'")

if [[ "$TEST_FILES" == "No test files found" ]]; then
    echo -e "${RED}Error: No test files were uploaded or found.${NC}"
    exit 1
else
    echo -e "${GREEN}Test files uploaded successfully.${NC}"
    echo "Uploaded files:"
    ssh ${SERVER_USER}@${SERVER_HOST} "ls -la ${REMOTE_DIR}/tests/test_*.py"
fi 