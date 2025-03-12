#!/run/current-system/sw/bin/bash

# Remote Docker Update Script for HomeLab Discord Bot
# This script updates the Docker container on a remote server

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

echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Remote Docker Update          ${NC}"
echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}Remote Host:${NC} $SERVER_HOST"
echo -e "${YELLOW}Remote Path:${NC} $SERVER_DIR"
echo -e "${YELLOW}Starting update at:${NC} $(date)"
echo -e "${YELLOW}=========================================================${NC}\n"

# Function to check if SSH connection is successful
check_ssh_connection() {
    echo -e "${YELLOW}Checking SSH connection...${NC}"
    if ssh "$SERVER_USER@$SERVER_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
        echo -e "${GREEN}SSH connection successful!${NC}\n"
        return 0
    else
        echo -e "${RED}Error: Could not connect to remote server via SSH.${NC}"
        echo "Please check your SSH credentials and server status."
        return 1
    fi
}

# Function to copy Docker related files to remote server
copy_docker_files() {
    echo -e "${YELLOW}Copying Docker files to remote server...${NC}"
    
    # Create a temporary directory
    TMP_DIR=$(mktemp -d)
    echo "Created temporary directory: ${TMP_DIR}"
    
    # Copy Docker related files
    cp compose/docker-compose.yml "${TMP_DIR}/"
    cp compose/Dockerfile "${TMP_DIR}/"
    cp app/bot/requirements.txt "${TMP_DIR}/"
    
    # Upload files to server
    ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${DOCKER_DIR}"
    scp "${TMP_DIR}/docker-compose.yml" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
    scp "${TMP_DIR}/Dockerfile" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
    
    # Upload requirements
    ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${SERVER_DIR}/app/bot"
    scp "${TMP_DIR}/requirements.txt" "${SERVER_USER}@${SERVER_HOST}:${SERVER_DIR}/app/bot/"
    
    # Clean up
    rm -rf "${TMP_DIR}"
    
    echo -e "${GREEN}Docker files copied successfully.${NC}\n"
    return 0
}

# Function to rebuild and restart Docker containers on remote server
rebuild_docker() {
    echo -e "${YELLOW}Rebuilding and restarting Docker containers...${NC}"
    
    # SSH into the remote server and rebuild the Docker containers
    ssh "${SERVER_USER}@${SERVER_HOST}" "cd ${DOCKER_DIR} && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error rebuilding Docker containers.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Docker containers rebuilt and restarted successfully.${NC}\n"
    return 0
}

# Function to wait for services to start
wait_for_services() {
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 20
    echo -e "${GREEN}Services should be running now.${NC}\n"
    return 0
}

# Main function
main() {
    # Check SSH connection
    check_ssh_connection
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Copy Docker files
    copy_docker_files
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Rebuild Docker
    rebuild_docker
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Wait for services to start
    wait_for_services
    
    echo -e "${GREEN}Docker update completed successfully.${NC}"
}

# Run the main function
main
