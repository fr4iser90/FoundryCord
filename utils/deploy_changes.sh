#!/usr/bin/env bash

# Deploy changes to the remote server before testing

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Server configuration
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
SERVER_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
DOCKER_DIR="${SERVER_DIR}/compose"

echo -e "${YELLOW}Deploying changes to ${SERVER_HOST}...${NC}"

# Create a temporary directory
TMP_DIR=$(mktemp -d)
echo "Created temporary directory: ${TMP_DIR}"

# Copy essential files to deploy
cp compose/docker-compose.yml "${TMP_DIR}/"
cp compose/Dockerfile "${TMP_DIR}/"
cp -r utils "${TMP_DIR}/"
cp app/bot/requirements.txt "${TMP_DIR}/"

# Upload files to server
echo "Uploading Docker Compose files..."
ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${DOCKER_DIR}"
scp "${TMP_DIR}/docker-compose.yml" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
scp "${TMP_DIR}/Dockerfile" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"

# Upload test scripts
echo "Uploading test scripts..."
ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${SERVER_DIR}/utils"
scp -r "${TMP_DIR}/utils/"* "${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}/utils/"

# Upload requirements
echo "Uploading requirements file..."
ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${SERVER_DIR}/app/bot"
scp "${TMP_DIR}/requirements.txt" "${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}/app/bot/"

# Clean up
rm -rf "${TMP_DIR}"

# Full Docker rebuild
echo -e "${YELLOW}Performing full Docker rebuild...${NC}"
ssh "${SERVER_USER}@${SERVER_HOST}" "cd ${DOCKER_DIR} && docker-compose down && docker-compose build --no-cache && docker-compose up -d"

echo "Waiting for services to start..."
sleep 15

echo -e "${GREEN}Deployment and rebuild completed successfully.${NC}" 