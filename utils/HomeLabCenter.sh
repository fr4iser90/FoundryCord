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

# Check for Docker .env file and load if it exists
if [ -f "./docker/.env" ]; then
    echo "Loading environment variables from docker/.env..."
    export $(grep -v '^#' ./docker/.env | xargs)
elif [ -f "../docker/.env" ]; then
    echo "Loading environment variables from ../docker/.env..."
    export $(grep -v '^#' ../docker/.env | xargs)
fi

# Global Variables
export RUN_LOCALLY=false
export AUTO_START=true
export AUTO_BUILD=true

# Source common utilities and configuration
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# Source UI modules
source "./utils/ui/display_functions.sh"
source "./utils/ui/input_functions.sh"

# Source function modules
source "./utils/functions/deployment_functions.sh"
source "./utils/functions/container_functions.sh"
source "./utils/functions/database_functions.sh"
source "./utils/functions/testing_functions.sh"
source "./utils/functions/development_functions.sh"
source "./utils/functions/log_functions.sh"

# Source menu modules
source "./utils/menus/main_menu.sh"
source "./utils/menus/deployment_menu.sh"
source "./utils/menus/container_menu.sh"
source "./utils/menus/database_menu.sh"
source "./utils/menus/testing_menu.sh"
source "./utils/menus/development_menu.sh"
source "./utils/menus/logs_menu.sh"
source "./utils/menus/env_files_menu.sh"
source "./utils/menus/auto_start_menu.sh"
source "./utils/menus/watch_menu.sh"

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    # Parse command line arguments
    parse_cli_args "$@"
    
    # Validate configuration first
    validate_config
    
    # Handle special execution modes
    if [ "$WATCH_CONSOLE" = true ]; then
        # Direct to deployment with monitoring
        print_info "Starting deployment with console monitoring..."
        run_deployment_with_monitoring "$WATCH_SERVICES"
        exit $?
    fi
    
    if [ "$INIT_ONLY" = true ]; then
        print_info "Running initialization only..."
        run_initial_setup
        exit $?
    fi
    
    # Check if this is the first run
    local first_run=false
    if [ ! -f "./utils/config/local_config.sh" ] || [ ! -f "${PROJECT_ROOT_DIR}/.env" ]; then
        first_run=true
    fi
    
    # For initial setup, check remote directories
    if [ "$first_run" = true ]; then
        echo "Checking remote directories..."
        if check_ssh_connection; then
            # Check project directory and create if needed
            if ! ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "test -d ${PROJECT_ROOT_DIR}" > /dev/null 2>&1; then
                echo -e "${YELLOW}Project directory not found: ${PROJECT_ROOT_DIR}${NC}"
                if get_yes_no "Would you like to create the directory structure?"; then
                    ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${PROJECT_ROOT_DIR}/{docker,app,web,backups}"
                    echo -e "${GREEN}Directory structure created.${NC}"
                fi
            fi
            
            # Check Docker directory and create if needed
            if ! ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "test -d ${DOCKER_DIR}" > /dev/null 2>&1; then
                echo -e "${YELLOW}Docker directory not found: ${DOCKER_DIR}${NC}"
                if get_yes_no "Would you like to create the Docker directory?"; then
                    ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${DOCKER_DIR}"
                    echo -e "${GREEN}Docker directory created.${NC}"
                fi
            fi
        fi
    fi
    
    # Display main menu
    show_main_menu
}

# Parse command line arguments
parse_cli_args() {
    for arg in "$@"; do
        case $arg in
            --auto-start)
                export AUTO_START=true
                ;;
            --no-auto-start)
                export AUTO_START=false
                ;;
            --watch-console)
                export WATCH_CONSOLE=true
                ;;
            --watch=*)
                export WATCH_SERVICES="${arg#*=}"
                export WATCH_CONSOLE=true
                ;;
            --feedback=*)
                export AUTO_START_FEEDBACK="${arg#*=}"
                ;;
            --init-only)
                export INIT_ONLY=true
                ;;
            --local)
                export RUN_LOCALLY=true
                ;;
            --env-file=*)
                export ENV_FILE="${arg#*=}"
                if [ -f "$ENV_FILE" ]; then
                    echo "Loading environment variables from $ENV_FILE..."
                    export $(grep -v '^#' "$ENV_FILE" | xargs)
                else
                    echo "Warning: Environment file $ENV_FILE not found"
                fi
                ;;
            *)
                # Pass other arguments to the common parser
                ;;
        esac
    done
}

# Run the main function with all command line arguments
main "$@"
