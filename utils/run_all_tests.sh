#!/usr/bin/env bash

# Master script to deploy changes, check services, upload tests, and run them

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Server configuration
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
DOCKER_DIR="/home/docker/docker/companion-management/homelab-discord-bot/compose"

echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Complete Testing Suite        ${NC}"
echo -e "${YELLOW}=========================================================${NC}"

# Check if scripts exist and are executable
for script in "utils/check_services.sh" "utils/upload_tests.sh" "utils/test.sh" "utils/deploy_changes.sh" "utils/update_remote_docker.sh"; do
    if [ ! -f "$script" ]; then
        echo -e "${RED}Error: Required script not found: ${script}${NC}"
        exit 1
    fi
    chmod +x "$script"
done

# Step 1: Deploy code changes
echo -e "\n${YELLOW}Step 1: Deploying code changes...${NC}"
./utils/deploy_changes.sh

# Step 2: Check if services are running
echo -e "\n${YELLOW}Step 2: Checking services...${NC}"
./utils/check_services.sh

# Ask to rebuild and restart services if they're not running or if we need to apply changes
if [ $? -ne 0 ]; then
    read -p "Some services are not running. Would you like to rebuild and restart the Docker stack? (y/n): " rebuild_services
    if [ "$rebuild_services" = "y" ]; then
        echo -e "${YELLOW}Rebuilding and restarting Docker services...${NC}"
        # Using update_remote_docker.sh for a complete rebuild
        ./utils/update_remote_docker.sh
        
        # Check again
        echo -e "${YELLOW}Checking services after rebuild...${NC}"
        ./utils/check_services.sh
    else
        read -p "Continue with testing anyway? (y/n): " continue_anyway
        if [ "$continue_anyway" != "y" ]; then
            echo -e "${RED}Testing aborted.${NC}"
            exit 1
        fi
    fi
fi

# Step 3: Upload test files
echo -e "\n${YELLOW}Step 3: Uploading test files...${NC}"
./utils/upload_tests.sh

# Step 4: Run tests
echo -e "\n${YELLOW}Step 4: Running tests...${NC}"
./utils/test.sh

echo -e "\n${GREEN}Complete testing process finished.${NC}" 