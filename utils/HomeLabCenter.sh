#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Central Management Interface
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

# Apply permissions to all scripts first 
echo "Setting executable permissions for all utility scripts..."
find utils -name "*.sh" -type f -exec chmod +x {} \;
find utils -name "*.py" -type f -exec chmod +x {} \;
echo "Permissions set successfully."

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Variables
# ------------------------------------------------------
MAIN_MENU_OPTION=""
SUB_MENU_OPTION=""
RUN_LOCALLY=false

# ------------------------------------------------------
# Functions
# ------------------------------------------------------

# Display header
show_header() {
    clear
    echo -e "${YELLOW}=========================================================${NC}"
    echo -e "${YELLOW}     HomeLab Discord Bot - Central Management Tool       ${NC}"
    echo -e "${YELLOW}=========================================================${NC}"
    echo -e "${YELLOW}Current Settings:${NC}"
    echo -e "  Server: ${GREEN}${SERVER_USER}@${SERVER_HOST}${NC}"
    echo -e "  Environment: ${GREEN}${ENVIRONMENT:-dev}${NC}"
    echo -e "${YELLOW}=========================================================${NC}"
    echo ""
}

# Validate configuration
validate_config() {
    show_header
    
    echo -e "Current configuration:"
    echo -e "  Server User: ${GREEN}${SERVER_USER}${NC}"
    echo -e "  Server Host: ${GREEN}${SERVER_HOST}${NC}"
    echo -e "  Server Port: ${GREEN}${SERVER_PORT}${NC}"
    echo -e "  Environment: ${GREEN}${ENVIRONMENT:-dev}${NC}"
    echo -e "  Remote Directory: ${GREEN}${REMOTE_DIR}${NC}"
    echo ""
    
    read -p "Are these settings correct? (Y/n): " confirm
    
    if [[ "${confirm,,}" == "n" ]]; then
        configure_settings
    fi
    
    # Check SSH connection
    echo -e "\nTesting SSH connection..."
    if ssh -q "${SERVER_USER}@${SERVER_HOST}" exit; then
        echo -e "${GREEN}SSH connection successful!${NC}"
    else
        echo -e "${RED}SSH connection failed!${NC}"
        echo "Please check your SSH configuration and server status."
        
        read -p "Do you want to run tools locally? (y/N): " run_local
        if [[ "${run_local,,}" == "y" ]]; then
            RUN_LOCALLY=true
            echo -e "${YELLOW}Running in local mode.${NC}"
        else
            echo "Returning to configuration..."
            configure_settings
        fi
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

# Configure settings
configure_settings() {
    show_header
    echo "Configure settings:"
    echo "------------------"
    
    read -p "Server User [${SERVER_USER}]: " input_user
    SERVER_USER=${input_user:-$SERVER_USER}
    
    read -p "Server Host [${SERVER_HOST}]: " input_host
    SERVER_HOST=${input_host:-$SERVER_HOST}
    
    read -p "Server Port [${SERVER_PORT}]: " input_port
    SERVER_PORT=${input_port:-$SERVER_PORT}
    
    read -p "Environment (dev/prod) [${ENVIRONMENT:-dev}]: " input_env
    ENVIRONMENT=${input_env:-${ENVIRONMENT:-dev}}
    
    # Save to local config
    echo "#!/usr/bin/env bash" > "./utils/config/local_config.sh"
    echo "" >> "./utils/config/local_config.sh"
    echo "# Local configuration overrides" >> "./utils/config/local_config.sh"
    echo "export SERVER_USER=\"${SERVER_USER}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_HOST=\"${SERVER_HOST}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_PORT=\"${SERVER_PORT}\"" >> "./utils/config/local_config.sh"
    echo "export ENVIRONMENT=\"${ENVIRONMENT}\"" >> "./utils/config/local_config.sh"
    
    echo -e "${GREEN}Settings saved to local_config.sh${NC}"
    echo ""
    
    # Re-source the config to apply changes
    source "./utils/config/config.sh"
}

# Show main menu
show_main_menu() {
    show_header
    
    echo "Main Menu:"
    echo "----------"
    echo "1. Deployment Tools"
    echo "2. Testing Tools"
    echo "3. Database Tools"
    echo "4. Development Tools"
    echo "5. Configure Settings"
    echo "0. Exit"
    echo ""
    
    read -p "Select an option: " MAIN_MENU_OPTION
    
    case "$MAIN_MENU_OPTION" in
        1) show_deployment_menu ;;
        2) show_testing_menu ;;
        3) show_database_menu ;;
        4) show_development_menu ;;
        5) configure_settings; show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            show_main_menu
            ;;
    esac
}

# Show deployment menu
show_deployment_menu() {
    show_header
    
    echo "Deployment Tools:"
    echo "-----------------"
    echo "1. Deploy to Server"
    echo "2. Update Docker Configuration"
    echo "3. Check Services"
    echo "4. Full Rebuild (CAUTION)"
    echo "9. Back to Main Menu"
    echo "0. Exit"
    echo ""
    
    read -p "Select an option: " SUB_MENU_OPTION
    
    case "$SUB_MENU_OPTION" in
        1) 
            echo -e "\n${YELLOW}Deploying to server...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot deploy in local mode.${NC}"
            else
                ./utils/deployment/deploy.sh
            fi
            read -p "Press Enter to continue..."
            show_deployment_menu
            ;;
        2) 
            echo -e "\n${YELLOW}Updating Docker configuration...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot update Docker in local mode.${NC}"
            else
                ./utils/deployment/update_docker.sh
            fi
            read -p "Press Enter to continue..."
            show_deployment_menu
            ;;
        3) 
            echo -e "\n${YELLOW}Checking services...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot check services in local mode.${NC}"
            else
                ./utils/deployment/check_services.sh
            fi
            read -p "Press Enter to continue..."
            show_deployment_menu
            ;;
        4) 
            echo -e "\n${RED}WARNING: Full rebuild will destroy all data!${NC}"
            read -p "Are you sure you want to proceed? (y/N): " confirm
            if [[ "${confirm,,}" == "y" ]]; then
                if [ "$RUN_LOCALLY" = true ]; then
                    echo -e "${RED}Cannot perform rebuild in local mode.${NC}"
                else
                    echo -e "${YELLOW}Performing full rebuild...${NC}"
                    ssh "${SERVER_USER}@${SERVER_HOST}" "cd ${REMOTE_DIR}/compose && docker-compose down"
                    ssh "${SERVER_USER}@${SERVER_HOST}" "docker volume rm \$(docker volume ls -q | grep homelab)"
                    ./utils/deployment/deploy.sh --rebuild
                fi
            fi
            read -p "Press Enter to continue..."
            show_deployment_menu
            ;;
        9) show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            show_deployment_menu
            ;;
    esac
}

# Show testing menu
show_testing_menu() {
    show_header
    
    echo "Testing Tools:"
    echo "--------------"
    echo "1. Run All Tests"
    echo "2. Upload Tests"
    echo "3. Test Server Environment"
    echo "4. Check Remote Services"
    echo "9. Back to Main Menu"
    echo "0. Exit"
    echo ""
    
    read -p "Select an option: " SUB_MENU_OPTION
    
    case "$SUB_MENU_OPTION" in
        1) 
            echo -e "\n${YELLOW}Running tests...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot run remote tests in local mode.${NC}"
            else
                ./utils/testing/run_tests.sh
            fi
            read -p "Press Enter to continue..."
            show_testing_menu
            ;;
        2) 
            echo -e "\n${YELLOW}Uploading tests...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot upload tests in local mode.${NC}"
            else
                ./utils/testing/upload_tests.sh
            fi
            read -p "Press Enter to continue..."
            show_testing_menu
            ;;
        3) 
            echo -e "\n${YELLOW}Running server tests...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot test server in local mode.${NC}"
            else
                ./utils/testing/test_server.sh
            fi
            read -p "Press Enter to continue..."
            show_testing_menu
            ;;
        4) 
            echo -e "\n${YELLOW}Checking remote services...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot check remote services in local mode.${NC}"
            else
                ./utils/testing/check_remote_services.sh
            fi
            read -p "Press Enter to continue..."
            show_testing_menu
            ;;
        9) show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            show_testing_menu
            ;;
    esac
}

# Show database menu
show_database_menu() {
    show_header
    
    echo "Database Tools:"
    echo "---------------"
    echo "1. Apply Alembic Migration"
    echo "2. Update Remote Database"
    echo "3. Database Category Fix"
    echo "9. Back to Main Menu"
    echo "0. Exit"
    echo ""
    
    read -p "Select an option: " SUB_MENU_OPTION
    
    case "$SUB_MENU_OPTION" in
        1) 
            echo -e "\n${YELLOW}Applying Alembic migration...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot apply migration in local mode.${NC}"
            else
                ./utils/database/update_alembic_migration.sh
            fi
            read -p "Press Enter to continue..."
            show_database_menu
            ;;
        2) 
            echo -e "\n${YELLOW}Updating remote database...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot update database in local mode.${NC}"
            else
                ./utils/database/update_remote_database.sh
            fi
            read -p "Press Enter to continue..."
            show_database_menu
            ;;
        3) 
            echo -e "\n${YELLOW}Applying category fix...${NC}"
            if [ "$RUN_LOCALLY" = true ]; then
                echo -e "${RED}Cannot apply fix in local mode.${NC}"
            else
                ./utils/database/category_v002.sh
            fi
            read -p "Press Enter to continue..."
            show_database_menu
            ;;
        9) show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            show_database_menu
            ;;
    esac
}

# Show development menu
show_development_menu() {
    show_header
    
    echo "Development Tools:"
    echo "------------------"
    echo "1. Generate Encryption Keys (Python Nix Shell)"
    echo "2. Initialize Test Environment"
    echo "9. Back to Main Menu"
    echo "0. Exit"
    echo ""
    
    read -p "Select an option: " SUB_MENU_OPTION
    
    case "$SUB_MENU_OPTION" in
        1) 
            echo -e "\n${YELLOW}Generating encryption keys...${NC}"
            if command -v nix-shell >/dev/null 2>&1; then
                nix-shell ./utils/development/python-shell.nix
            else
                echo -e "${RED}Error: nix-shell not installed.${NC}"
                echo "Please install Nix from https://nixos.org/download.html"
            fi
            read -p "Press Enter to continue..."
            show_development_menu
            ;;
        2) 
            echo -e "\n${YELLOW}Initializing test environment...${NC}"
            ./utils/testing/init_test_env.sh
            read -p "Press Enter to continue..."
            show_development_menu
            ;;
        9) show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            show_development_menu
            ;;
    esac
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    validate_config
    show_main_menu
}

# Run the main function
main
