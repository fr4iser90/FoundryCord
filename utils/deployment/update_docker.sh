#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Docker Configuration Update
# =======================================================

# Source configuration
source "$(dirname "$0")/../config/config.sh"
source "$(dirname "$0")/../lib/common.sh"

# Header
echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Docker Configuration Update   ${NC}"
echo -e "${YELLOW}=========================================================${NC}"

# Check SSH connection
if ! check_ssh_connection; then
    echo -e "${RED}Cannot update Docker configuration.${NC}"
    exit 1
fi

# Function to update bot Docker configuration
update_bot_docker() {
    echo -e "\n${YELLOW}Updating Bot Docker Configuration...${NC}"
    
    # Create directory if it doesn't exist
    run_remote_command "mkdir -p ${DOCKER_DIR}"
    
    # Copy Docker files
    echo "Copying Bot Docker configuration files..."
    scp -r "${LOCAL_GIT_DIR}/docker/bot/"* "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
    
    echo -e "${GREEN}Bot Docker configuration updated successfully!${NC}"
}

# Function to update web Docker configuration
update_web_docker() {
    echo -e "\n${YELLOW}Checking for Web Docker Configuration...${NC}"
    
    # Check if web docker files exist in local git directory
    if [ -d "${LOCAL_GIT_DIR}/docker/web" ]; then
        echo "Web Docker configuration found. Updating..."
        
        # Create directory if it doesn't exist
        run_remote_command "mkdir -p ${DOCKER_DIR}"
        
        # Copy Docker files
        echo "Copying Web Docker configuration files..."
        scp -r "${LOCAL_GIT_DIR}/docker/web/"* "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
        
        echo -e "${GREEN}Web Docker configuration updated successfully!${NC}"
    else
        echo "No web Docker configuration found. Skipping."
    fi
}

# Main function
main() {
    # Update bot Docker configuration
    update_bot_docker
    
    # Update web Docker configuration
    update_web_docker
    
    echo -e "\n${GREEN}Docker configuration update completed!${NC}"
    
    # Ask if user wants to rebuild containers
    read -p "Do you want to rebuild containers now? (y/N): " rebuild
    if [[ "${rebuild,,}" == "y" ]]; then
        echo "Rebuilding containers..."
        run_remote_command "cd ${DOCKER_DIR} && ${BOT_COMPOSE_DOWN} && ${BOT_COMPOSE_BUILD_NOCACHE} && ${BOT_COMPOSE_UP}"
        
        if run_remote_command "test -f ${WEB_COMPOSE_FILE}" "true"; then
            run_remote_command "cd ${DOCKER_DIR} && ${WEB_COMPOSE_DOWN} && ${WEB_COMPOSE_BUILD_NOCACHE} && ${WEB_COMPOSE_UP}"
        fi
        
        echo -e "${GREEN}Containers rebuilt successfully!${NC}"
    fi
}

# Run the main function
main 