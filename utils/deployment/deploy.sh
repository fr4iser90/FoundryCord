#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Script
# =======================================================

# Source configuration
source "$(dirname "$0")/../config/config.sh"
source "$(dirname "$0")/../lib/common.sh"

# Header
echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Deployment Tool               ${NC}"
echo -e "${YELLOW}=========================================================${NC}"

# Check SSH connection
if ! check_ssh_connection; then
    echo -e "${RED}Cannot proceed with deployment.${NC}"
    exit 1
fi

# Function to deploy bot application
deploy_bot() {
    echo -e "\n${YELLOW}Deploying Discord Bot Application...${NC}"
        
    # 2. Copy bot application files
    echo "Copying bot application files..."
    scp -r "${LOCAL_GIT_DIR}/app/"* "${SERVER_USER}@${SERVER_HOST}:${APP_DIR}/"
    
    # 3. Copy Docker files
    echo "Copying Docker configuration files..."
    
    scp "${LOCAL_GIT_DIR}/docker/."* "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
    #scp "${LOCAL_GIT_DIR}/docker/." "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"

    # 4. Deploy the containers
    echo "Deploying Docker containers..."
    if [ "${REBUILD_ON_DEPLOY}" = "true" ]; then
        run_remote_command "cd ${PROJECT_ROOT_DIR}/docker && docker compose down && docker compose build --no-cache && docker compose up -d"
    else
        run_remote_command "cd ${PROJECT_ROOT_DIR}/docker && docker compose up -d --build"
    fi
    
    echo -e "${GREEN}Bot deployment completed successfully!${NC}"
}


# Main deployment function
main() {
    # 1. Deploy bot
    deploy_bot
    
    # 3. Check services
    echo -e "\n${YELLOW}Checking services...${NC}"
    sleep 5  # Give services time to start
    "$(dirname "$0")/check_services.sh"
    
    echo -e "\n${GREEN}Deployment completed successfully!${NC}"
}

# Run the main function
main 