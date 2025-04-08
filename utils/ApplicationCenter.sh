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

# Check if local_config.sh exists, if not create it from example
if [ ! -f "./utils/config/local_config.sh" ]; then
    echo "No local configuration found. Creating from example..."
    if [ -f "./utils/config/local_config.example.sh" ]; then
        cp "./utils/config/local_config.example.sh" "./utils/config/local_config.sh"
        # Replace $(date) with actual date in the copied file
        sed -i "s/\$(date)/$(date)/g" "./utils/config/local_config.sh"
        echo "✅ Created local_config.sh from example."
        echo "⚠️ Please review and edit ./utils/config/local_config.sh to match your environment before proceeding."
        echo "    You can press Ctrl+C now to exit and edit the file,"
        echo "    or continue with default values."
        read -p "Press Enter to continue or Ctrl+C to exit..." response
    else
        echo "❌ Error: Could not find local_config.example.sh!"
        echo "Please create ./utils/config/local_config.sh manually before continuing."
        exit 1
    fi
fi

# Check for Docker .env file and load if it exists
if [ -f "../docker/.env" ]; then
    echo "Loading environment variables from ../docker/.env..."
    # Only export valid VAR=VALUE lines, properly handling comments
    set -a
    source <(grep -E '^[A-Za-z0-9_]+=.+' ../docker/.env | sed '/^#/d')
    set +a
fi

# Global Variables
export RUN_LOCALLY=false
export AUTO_START=true
export AUTO_BUILD=true
export REMOVE_VOLUMES=false
export SKIP_CONFIRMATION=false
export DIRECT_DEPLOY=false

# Parse command line arguments for local mode
for arg in "$@"; do
    case $arg in
        --local)
            export RUN_LOCALLY=true
            echo "Running in local mode with project directory: $LOCAL_PROJECT_DIR"
            shift
            ;;
    esac
done

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
    
    # Handle direct deployment options first (bypass menus)
    if [ "$DIRECT_DEPLOY" = true ]; then
        # Skip showing any menus and run the requested deployment directly
        exit $?
    fi
    
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
        
    # Display main menu
    show_main_menu
}

# Parse command line arguments
parse_cli_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            # Development hot-reload options
            --local-web-replace)
                RUN_LOCALLY=true
                hot_reload_web
                exit $?
                ;;
            --local-bot-replace)
                RUN_LOCALLY=true
                hot_reload_bot
                exit $?
                ;;
            --local-shared-replace)
                RUN_LOCALLY=true
                hot_reload_shared
                exit $?
                ;;
            --local-all-replace)
                RUN_LOCALLY=true
                hot_reload_web
                hot_reload_bot
                hot_reload_shared
                exit $?
                ;;
            
            # Existing options...
            --init-only) INIT_ONLY=true ;;
            --skip-confirmation) SKIP_CONFIRMATION=true ;;
            --remove-volumes) REMOVE_VOLUMES=true ;;
            --env-file=*) 
                ENV_FILE="${1#*=}"
                [ -f "$ENV_FILE" ] && source_env_file "$ENV_FILE"
                ;;
            
            # Deployment modes
            --quick-deploy) DIRECT_DEPLOY=true; run_quick_deploy ;;
            --quick-deploy-attach) DIRECT_DEPLOY=true; run_quick_deploy_attach ;;
            --partial-deploy) DIRECT_DEPLOY=true; run_partial_deploy ;;
            --deploy-with-auto-start) DIRECT_DEPLOY=true; run_quick_deploy_with_auto_start ;;
            --full-reset)
                DIRECT_DEPLOY=true
                if [ "$SKIP_CONFIRMATION" != "true" ]; then
                    print_error "⚠️ WARNING: This will COMPLETELY ERASE your database!"
                    if ! get_confirmed_input "Are you ABSOLUTELY sure?" "DELETE"; then
                        print_info "Cancelled."
                        exit 1
                    fi
                fi
                run_full_reset_deploy
                ;;
            --deploy-with-monitoring)
                DIRECT_DEPLOY=true
                run_deployment_with_monitoring "all"
                ;;
            --watch-console) WATCH_CONSOLE=true ;;
            --watch=*) WATCH_SERVICES="${1#*=}"; WATCH_CONSOLE=true ;;

            # Testing
            --test-ALL) DIRECT_ACTION=true; run_tests_with_docker_container "all"; exit $? ;;
            --test-unit) DIRECT_ACTION=true; run_unit_tests; exit $? ;;
            --test-integration) DIRECT_ACTION=true; run_integration_tests; exit $? ;;
            --test-system) DIRECT_ACTION=true; run_system_tests; exit $? ;;
            --test-ordered) DIRECT_ACTION=true; run_ordered_tests; exit $? ;;
            --test-simple) run_simple_test; exit 0 ;;
            --test-dashboard) run_dashboard_tests; exit 0 ;;
            --sequential-tests) DIRECT_ACTION=true; run_sequential_tests; exit $? ;;
            --sync-results) DIRECT_ACTION=true; sync_test_results; exit 0 ;;

            # Unknown argument
            *)
                echo "⚠️ Unknown argument: $1"
                ;;
        esac
        shift
    done
}

# Run the main function with all command line arguments
main "$@"
