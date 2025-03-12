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
    
    # 1. DIRECTLY COPY .ENV FILE - NO CHECKS
    echo -e "\n${YELLOW}Copying .env file...${NC}"
    scp "${LOCAL_GIT_DIR}/docker/bot/.env" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/.env"
    echo -e "${GREEN}.env file copied.${NC}"
    
    # 2. Copy bot application files
    echo "Copying bot application files..."
    scp -r "${LOCAL_GIT_DIR}/app/bot/"* "${SERVER_USER}@${SERVER_HOST}:${BOT_DIR}/"
    
    # 3. Copy Docker files
    echo "Copying Docker configuration files..."
    
    # Copy the individual docker files from bot directory
    scp "${LOCAL_GIT_DIR}/docker/bot/Dockerfile" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    scp "${LOCAL_GIT_DIR}/docker/bot/entrypoint.sh" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    scp "${LOCAL_GIT_DIR}/docker/bot/init-db.sh" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    
    # Copy the main docker-compose.yml to the correct location
    echo "Copying main docker-compose.yml file..."
    scp "${LOCAL_GIT_DIR}/docker/docker-compose.yml" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/docker-compose.yml"
    scp "${LOCAL_GIT_DIR}/docker/bot/.env" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/.env"
    scp "${LOCAL_GIT_DIR}/docker/bot/.env" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/bot/.env"
    scp "${LOCAL_GIT_DIR}/docker/bot/.env" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/web/.env"

    # 4. Deploy the containers
    echo "Deploying Docker containers..."
    if [ "${REBUILD_ON_DEPLOY}" = "true" ]; then
        run_remote_command "cd ${PROJECT_ROOT_DIR}/docker && docker compose down && docker compose build --no-cache && docker compose up -d"
    else
        run_remote_command "cd ${PROJECT_ROOT_DIR}/docker && docker compose up -d --build"
    fi
    
    echo -e "${GREEN}Bot deployment completed successfully!${NC}"
}

# Function to deploy web application (if available)
deploy_web() {
    echo -e "\n${YELLOW}Checking for Web Application...${NC}"
    
    # Check if web docker-compose file exists in local git directory
    if [ -f "${LOCAL_GIT_DIR}/docker/web/docker-compose.web.yml" ]; then
        echo "Web application found. Deploying..."
        
        # 1. Copy web .env file directly
        if [ -f "${LOCAL_GIT_DIR}/docker/web/.env" ]; then
            echo "Copying web .env file..."
            scp "${LOCAL_GIT_DIR}/docker/web/.env" "${SERVER_USER}@${SERVER_HOST}:${WEB_DOCKER_DIR}/.env"
        fi
        
        # 2. Copy web application files if they exist
        if [ -d "${LOCAL_GIT_DIR}/app/web" ]; then
            echo "Copying web application files..."
            scp -r "${LOCAL_GIT_DIR}/app/web/"* "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/"
        fi
        
        # 3. Copy Docker files
        echo "Copying web Docker configuration files..."
        scp "${LOCAL_GIT_DIR}/docker/web/docker-compose.web.yml" "${SERVER_USER}@${SERVER_HOST}:${WEB_DOCKER_DIR}/"
        scp "${LOCAL_GIT_DIR}/docker/web/Dockerfile.web" "${SERVER_USER}@${SERVER_HOST}:${WEB_DOCKER_DIR}/"
        
        # 4. Deploy the containers
        echo "Deploying web Docker containers..."
        if [ "${REBUILD_ON_DEPLOY}" = "true" ]; then
            run_remote_command "cd ${WEB_DOCKER_DIR} && docker compose -f docker-compose.web.yml down && docker compose -f docker-compose.web.yml build --no-cache && docker compose -f docker-compose.web.yml up -d"
        else
            run_remote_command "cd ${WEB_DOCKER_DIR} && docker compose -f docker-compose.web.yml up -d --build"
        fi
        
        echo -e "${GREEN}Web deployment completed successfully!${NC}"
    else
        echo "No web application found. Skipping web deployment."
    fi
}

# Main deployment function
main() {
    # 1. Deploy bot
    deploy_bot
    
    # 2. Deploy web (if available)
    deploy_web
    
    # 3. Check services
    echo -e "\n${YELLOW}Checking services...${NC}"
    sleep 5  # Give services time to start
    "$(dirname "$0")/check_services.sh"
    
    echo -e "\n${GREEN}Deployment completed successfully!${NC}"
}

# Run the main function
main 