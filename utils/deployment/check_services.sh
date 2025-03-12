#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Service Status Check with Auto-Restart
# =======================================================

# Source configuration
source "$(dirname "$0")/../config/config.sh"
source "$(dirname "$0")/../lib/common.sh"

# Header
echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Service Status Check          ${NC}"
echo -e "${YELLOW}=========================================================${NC}"

# Check SSH connection
if ! check_ssh_connection; then
    echo -e "${RED}Cannot check services.${NC}"
    exit 1
fi

# Function to restart bot services if needed
restart_bot_services() {
    local rebuild="${1:-false}"
    
    echo -e "\n${YELLOW}Starting bot services...${NC}"
    
    if [ "$rebuild" = "true" ]; then
        echo "Rebuilding and starting bot services..."
        run_remote_command "cd ${BOT_DOCKER_DIR} && ${BOT_COMPOSE_DOWN} && ${BOT_COMPOSE_BUILD_NOCACHE} && ${BOT_COMPOSE_UP}"
    else
        echo "Starting bot services without rebuild..."
        run_remote_command "cd ${BOT_DOCKER_DIR} && ${BOT_COMPOSE_UP}"
    fi
    
    # Give services time to start
    echo "Waiting for services to start..."
    sleep 10
    
    # Recheck status
    echo -e "\n${YELLOW}Rechecking Bot Services...${NC}"
    check_bot_status
}

# Function to restart web services if needed
restart_web_services() {
    local rebuild="${1:-false}"
    
    echo -e "\n${YELLOW}Starting web services...${NC}"
    
    # Check if web compose file exists first
    if ! run_remote_command "test -f ${WEB_COMPOSE_FILE}" "true"; then
        echo -e "${YELLOW}Web services not deployed. Skipping...${NC}"
        return
    fi
    
    if [ "$rebuild" = "true" ]; then
        echo "Rebuilding and starting web services..."
        run_remote_command "cd ${WEB_DOCKER_DIR} && ${WEB_COMPOSE_DOWN} && ${WEB_COMPOSE_BUILD_NOCACHE} && ${WEB_COMPOSE_UP}"
    else
        echo "Starting web services without rebuild..."
        run_remote_command "cd ${WEB_DOCKER_DIR} && ${WEB_COMPOSE_UP}"
    fi
    
    # Give services time to start
    echo "Waiting for services to start..."
    sleep 10
    
    # Recheck status
    echo -e "\n${YELLOW}Rechecking Web Services...${NC}"
    check_web_status
}

# Function to check bot services status only (no prompt)
check_bot_status() {
    local bot_running=false
    local postgres_running=false
    local redis_running=false
    
    # Check Discord Bot
    if run_remote_command "docker ps | grep -q ${BOT_CONTAINER}" "true"; then
        echo -e "${GREEN}✓ ${BOT_CONTAINER} is running${NC}"
        bot_running=true
    else
        echo -e "${RED}✗ ${BOT_CONTAINER} is NOT running${NC}"
    fi
    
    # Check Postgres
    if run_remote_command "docker ps | grep -q ${POSTGRES_CONTAINER}" "true"; then
        echo -e "${GREEN}✓ ${POSTGRES_CONTAINER} is running${NC}"
        postgres_running=true
    else
        echo -e "${RED}✗ ${POSTGRES_CONTAINER} is NOT running${NC}"
    fi
    
    # Check Redis
    if run_remote_command "docker ps | grep -q ${REDIS_CONTAINER}" "true"; then
        echo -e "${GREEN}✓ ${REDIS_CONTAINER} is running${NC}"
        redis_running=true
    else
        echo -e "${RED}✗ ${REDIS_CONTAINER} is NOT running${NC}"
    fi
    
    # Return success if all are running
    if [ "$bot_running" = true ] && [ "$postgres_running" = true ] && [ "$redis_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check web services status only (no prompt)
check_web_status() {
    local web_running=false
    local web_db_running=false
    
    # Check if web compose file exists first
    if ! run_remote_command "test -f ${WEB_COMPOSE_FILE}" "true"; then
        echo -e "${YELLOW}Web services not deployed. Skipping...${NC}"
        return 0
    fi
    
    # Check Web Container
    if run_remote_command "docker ps | grep -q ${WEB_CONTAINER}" "true"; then
        echo -e "${GREEN}✓ ${WEB_CONTAINER} is running${NC}"
        web_running=true
    else
        echo -e "${RED}✗ ${WEB_CONTAINER} is NOT running${NC}"
    fi
    
    # Check Web DB
    if run_remote_command "docker ps | grep -q ${WEB_DB_CONTAINER}" "true"; then
        echo -e "${GREEN}✓ ${WEB_DB_CONTAINER} is running${NC}"
        web_db_running=true
    else
        echo -e "${RED}✗ ${WEB_DB_CONTAINER} is NOT running${NC}"
    fi
    
    # Return success if all are running
    if [ "$web_running" = true ] && [ "$web_db_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check bot services with restart option
check_bot_services() {
    echo -e "\n${YELLOW}Checking Bot Services...${NC}"
    
    # Check status
    if check_bot_status; then
        # Services are running, ask to view logs
        read -p "Do you want to see the recent bot logs? (y/N): " show_logs
        if [[ "${show_logs,,}" == "y" ]]; then
            run_remote_command "${BOT_LOGS} --tail 50"
        fi
    else
        # Services not running, offer to start them
        read -p "Some bot services are not running. Do you want to start them? (Y/n): " start_services
        
        if [[ "${start_services,,}" != "n" ]]; then
            read -p "Do you want to rebuild the containers first? (y/N): " rebuild_first
            
            if [[ "${rebuild_first,,}" == "y" ]]; then
                restart_bot_services "true"
            else
                restart_bot_services "false"
            fi
        fi
    fi
}

# Function to check web services with restart option
check_web_services() {
    echo -e "\n${YELLOW}Checking Web Services...${NC}"
    
    # Check if web compose file exists first
    if ! run_remote_command "test -f ${WEB_COMPOSE_FILE}" "true"; then
        echo -e "${YELLOW}Web services not deployed. Skipping...${NC}"
        return
    fi
    
    # Check status
    if check_web_status; then
        # Services are running, ask to view logs
        read -p "Do you want to see the recent web logs? (y/N): " show_logs
        if [[ "${show_logs,,}" == "y" ]]; then
            run_remote_command "${WEB_LOGS} --tail 50"
        fi
    else
        # Services not running, offer to start them
        read -p "Some web services are not running. Do you want to start them? (Y/n): " start_services
        
        if [[ "${start_services,,}" != "n" ]]; then
            read -p "Do you want to rebuild the containers first? (y/N): " rebuild_first
            
            if [[ "${rebuild_first,,}" == "y" ]]; then
                restart_web_services "true"
            else
                restart_web_services "false"
            fi
        fi
    fi
}

# Main function
main() {
    # Check bot services
    check_bot_services
    
    # Check web services
    check_web_services
    
    echo -e "\n${GREEN}Service check completed.${NC}"
}

# Run the main function
main 