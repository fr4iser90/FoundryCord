#!/usr/bin/env bash

# =======================================================
# Application Center - Central Management Interface
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

# Apply permissions to all scripts first 
echo "Setting executable permissions for all utility scripts..."
find utils -name "*.sh" -type f -exec chmod +x {} \;
find utils -name "*.py" -type f -exec chmod +x {} \;
echo "Permissions set successfully."

# Ensure project_config.sh exists manually before running.
if [ ! -f "./utils/config/project_config.sh" ]; then
    echo "❌ Error: Project configuration file ./utils/config/project_config.sh not found!"
    echo "Please create this file (e.g., by copying from another project or manually) before running the Application Center."
    exit 1
fi

# Check for Docker .env file and load if it exists
# Load from project root first, then docker dir
if [ -f "./.env" ]; then
    echo "Loading environment variables from ./.env..."
    set -a
    source <(grep -vE '^\s*(#|$)' ./.env)
    set +a
elif [ -f "./docker/.env" ]; then 
    echo "Loading environment variables from ./docker/.env..."
    set -a
    source <(grep -vE '^\s*(#|$)' ./docker/.env)
    set +a
fi

# Global Variables
export RUN_LOCALLY=true
export AUTO_START=true
export AUTO_BUILD=true
export REMOVE_VOLUMES=false
export SKIP_CONFIRMATION=false
export DIRECT_DEPLOY=false
export DOCKER_PROFILE="" # Initialize Docker profile variable

# Parse command line arguments for local mode
for arg in "$@"; do
    case $arg in
        --remote)
            export RUN_LOCALLY=false
            echo "Running in remote mode with server: $SERVER_HOST"
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
    # Parse command line arguments first to potentially set RUN_LOCALLY etc.
    parse_cli_args "$@"
    
    # Validate configuration (which is now loaded via config.sh -> project_config.sh)
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
            # >>> Add profile handling here <<<
            --profile=*) 
                DOCKER_PROFILE="${1#*=}"
                # Validate profile maybe? (cpu, gpu-nvidia, gpu-amd)
                # TODO: Add validation if needed
                echo "Using Docker profile: ${DOCKER_PROFILE}"
                ;;

            # Development hot-reload options (Generic)
            --hot-reload=*) 
                local target="${1#*=}"
                # Check if target is valid (from HOT_RELOAD_TARGETS in config)
                if [[ " ${HOT_RELOAD_TARGETS} " =~ " ${target} " ]]; then
                    RUN_LOCALLY=true # Hot-reload only makes sense locally
                    print_info "Initiating hot-reload for target: ${target}..."
                    run_hot_reload "${target}" # Assumes this function exists in development_functions.sh
                    exit $?
                else
                    print_error "Invalid hot-reload target: '${target}'."
                    print_info "Valid targets are: ${HOT_RELOAD_TARGETS}"
                    exit 1
                fi
                ;;
            --hot-reload-all)
                RUN_LOCALLY=true # Hot-reload only makes sense locally
                print_info "Initiating hot-reload for all targets: ${HOT_RELOAD_TARGETS}..."
                for target in ${HOT_RELOAD_TARGETS}; do
                    run_hot_reload "${target}" # Assumes this function exists
                done
                exit $?
                ;;

            # Existing options...
            --local) # Ensure --local is handled *after* --profile and hot-reload
                export RUN_LOCALLY=true
                echo "Running in local mode with project directory: $LOCAL_PROJECT_DIR"
                ;;
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
                # Avoid erroring out if it's just the --local flag which is handled elsewhere
                if [ "$1" != "--local" ]; then 
                    echo "⚠️ Unknown argument: $1"
                fi
                ;;
        esac
        shift
    done
}

# Run the main function with all command line arguments
main "$@"
