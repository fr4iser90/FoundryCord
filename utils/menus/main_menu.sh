#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Main Menu
# =======================================================

# Show main menu
show_main_menu() {
    show_header
    
    # Check if this is a first run/setup situation
    local is_first_setup=false
    
    # Run a check to see if Docker files exist on remote server
    if [ "$RUN_LOCALLY" = false ]; then
        if ! run_remote_command "test -d ${DOCKER_DIR}" "silent"; then
            is_first_setup=true
        fi
        
        if ! run_remote_command "test -f ${DOCKER_DIR}/docker-compose.yml" "silent"; then
            is_first_setup=true
        fi
    fi
    
    if [ "$is_first_setup" = true ]; then
        print_section_header "Initial Setup Required"
        print_info "It appears this is your first time running the HomeLab Discord Bot."
        print_info "Let's set up the environment on your remote server."
        echo ""
        
        print_menu_item "1" "Run Initial Setup (creates directories and copies files)"
        print_menu_item "2" "Configure Settings"
        print_menu_item "3" "Advanced Menu (skip setup)"
        print_menu_item "0" "Exit"
        
        echo ""
        
        local choice=$(get_numeric_input "Select an option: ")
        
        case $choice in
            1)
                run_initial_setup
                ;;
            2)
                configure_settings
                show_main_menu
                ;;
            3)
                show_regular_menu
                ;;
            0)
                clear
                echo "Exiting. Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                press_enter_to_continue
                show_main_menu
                ;;
        esac
    else
        show_regular_menu
    fi
}

# Show regular main menu (when already set up)
show_regular_menu() {
    print_section_header "Main Menu"
    print_menu_item "1" "Deployment Tools"
    print_menu_item "2" "Container Management"
    print_menu_item "3" "Testing Tools"
    print_menu_item "4" "Database Tools" 
    print_menu_item "5" "Development Tools"
    print_menu_item "6" "Configure Settings"
    print_menu_item "7" "Manage Environment Files"
    print_menu_item "8" "View Logs"
    print_menu_item "9" "Real-time Monitoring"
    print_menu_item "0" "Exit"
    
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case $choice in
        1)
            show_deployment_menu
            ;;
        2)
            show_container_menu
            ;;
        3)
            show_testing_menu
            ;;
        4)
            show_database_menu
            ;;
        5)
            show_development_menu
            ;;
        6)
            configure_settings
            show_main_menu
            ;;
        7)
            show_env_files_menu
            ;;
        8)
            show_logs_menu
            ;;
        9)
            show_watch_menu
            ;;
        0)
            clear
            echo "Exiting. Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            press_enter_to_continue
            show_main_menu
            ;;
    esac
}

# Run initial setup to properly configure the remote server
run_initial_setup() {
    clear
    print_section_header "Initial Setup"
    
    print_info "Setting up the HomeLab Discord Bot on your remote server..."
    
    # Check if server is accessible
    if ! check_ssh_connection; then
        print_error "Cannot connect to server. Please check your connection settings."
        
        if get_yes_no "Would you like to configure connection settings now?"; then
            configure_settings
            
            # Try again
            if ! check_ssh_connection; then
                print_error "Still cannot connect to server."
                return 1
            fi
        else
            return 1
        fi
    }
    
    # Check if Docker is installed on remote server
    print_info "Checking for Docker installation..."
    if ! run_remote_command "command -v docker" "silent" | grep -q docker; then
        print_error "Docker is not installed on the remote server."
        print_info "Please install Docker on your server before continuing."
        return 1
    else
        print_success "Docker is installed on the remote server."
    fi
    
    # Check if Docker Compose is installed
    print_info "Checking for Docker Compose installation..."
    if ! run_remote_command "command -v docker compose" "silent" | grep -q docker; then
        print_warning "Docker Compose V2 not found, checking for docker-compose..."
        
        if ! run_remote_command "command -v docker-compose" "silent" | grep -q docker-compose; then
            print_error "Docker Compose is not installed on the remote server."
            print_info "Please install Docker Compose on your server before continuing."
            return 1
        else
            print_success "Docker Compose V1 is installed on the remote server."
            print_info "Consider upgrading to Docker Compose V2 for better performance."
            # Update DOCKER_COMPOSE_CMD for V1
            export DOCKER_COMPOSE_CMD="docker-compose"
        fi
    else
        print_success "Docker Compose V2 is installed on the remote server."
    fi
    
    # 1. Create necessary directories on remote server with proper permissions
    print_info "Creating directory structure with proper permissions..."
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/{docker,app,backups,utils/config} && chmod -R 775 ${PROJECT_ROOT_DIR}"
    
    # 2. Copy Docker configuration files
    print_info "Copying Docker configuration files..."
    if [ -d "${LOCAL_GIT_DIR}/docker" ]; then
        # First ensure the target directory has proper permissions
        run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/docker && chmod -R 775 ${PROJECT_ROOT_DIR}/docker"
        # Copy the files
        scp -r "${LOCAL_GIT_DIR}/docker/"* "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/"
        
        # Copy .env file if it exists
        if [ -f "${LOCAL_GIT_DIR}/.env" ]; then
            print_info "Copying main .env file from project root..."
            scp "${LOCAL_GIT_DIR}/.env" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/.env"
        fi
        
        if [ -f "${LOCAL_GIT_DIR}/docker/.env" ]; then
            print_info "Copying docker/.env file..."
            scp "${LOCAL_GIT_DIR}/docker/.env" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/docker/.env"
        fi
    else
        print_error "Local docker directory not found at ${LOCAL_GIT_DIR}/docker"
        print_info "Creating empty Docker directory structure..."
        run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/docker && chmod -R 775 ${PROJECT_ROOT_DIR}/docker"
    fi
    
    # 3. Copy application files
    print_info "Copying application files..."
    if [ -d "${LOCAL_GIT_DIR}/app" ]; then
        # First ensure the target directory has proper permissions
        run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/app/{bot,web,postgres} && chmod -R 775 ${PROJECT_ROOT_DIR}/app"
        # Copy the files
        scp -r "${LOCAL_GIT_DIR}/app/"* "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/"
    else
        print_error "Local app directory not found at ${LOCAL_GIT_DIR}/app"
        print_info "Creating empty app directory structure..."
        run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/app/{bot,web,postgres} && chmod -R 775 ${PROJECT_ROOT_DIR}/app"
    fi
    
    # 4. Check if we have .env files, create them if needed
    local need_env_setup=true
    
    # Check if the main .env file was copied earlier
    if run_remote_command "test -f ${PROJECT_ROOT_DIR}/.env" "silent"; then
        print_success ".env file found in project root"
        need_env_setup=false
        
        # Copy to docker directory as well if it doesn't exist there
        if ! run_remote_command "test -f ${DOCKER_DIR}/.env" "silent"; then
            print_info "Copying .env file to Docker directory..."
            run_remote_command "cp ${PROJECT_ROOT_DIR}/.env ${DOCKER_DIR}/.env"
        fi
    elif run_remote_command "test -f ${DOCKER_DIR}/.env" "silent"; then
        print_success ".env file found in Docker directory"
        need_env_setup=false
        
        # Copy to project root as well
        print_info "Copying .env file to project root..."
        run_remote_command "cp ${DOCKER_DIR}/.env ${PROJECT_ROOT_DIR}/.env"
    fi
    
    # Ask if user wants to create .env files if they don't exist
    if [ "$need_env_setup" = true ]; then
        if get_yes_no "No .env file found. Would you like to create one now?"; then
            create_env_file
        else
            print_warning "No .env file created. You'll need to create one manually before starting services."
        fi
    fi
    
    # 5. Initialize auto-start configuration
    print_info "Setting up auto-start configuration..."
    if get_yes_no "Do you want to enable auto-start for services?"; then
        AUTO_START="true"
        AUTO_START_SERVICES="all"
        
        # Ask about services if they want specifics
        if ! get_yes_no "Do you want to auto-start all services?"; then
            print_info "Please select which services to auto-start in the next menu."
            AUTO_START_SERVICES="bot,postgres,redis"
        fi
        
        # Ask about build options
        if get_yes_no "Do you want to enable automatic rebuilding before starting?"; then
            AUTO_BUILD_ENABLED="true"
        else
            AUTO_BUILD_ENABLED="false"
        fi
        
        # Ask about feedback level
        echo "Select feedback level during auto-start:"
        echo "1. None - No feedback"
        echo "2. Minimal - Basic status information"
        echo "3. Verbose - Detailed logs and status"
        local feedback_choice=$(get_numeric_input "Select an option: ")
        
        case $feedback_choice in
            1) AUTO_START_FEEDBACK="none" ;;
            2) AUTO_START_FEEDBACK="minimal" ;;
            3) AUTO_START_FEEDBACK="verbose" ;;
            *) AUTO_START_FEEDBACK="minimal" ;;
        esac
        
        # Save auto-start configuration
        save_auto_start_config "${AUTO_START}" "${AUTO_START_SERVICES}" "${AUTO_START_FEEDBACK}"
    else
        AUTO_START="false"
        save_auto_start_config "false" "none" "none"
    fi
    
    # 6. Ask if user wants to build and start containers
    if get_yes_no "Would you like to build and start the containers now?"; then
        print_info "Building and starting containers..."
        run_partial_deploy
    fi
    
    print_success "Initial setup completed!"
    print_info "You can now use the main menu to manage your HomeLab Discord Bot."
    
    press_enter_to_continue
    show_main_menu
}

# Configure settings
configure_settings() {
    clear
    print_section_header "Configuration Settings"
    
    echo "Current configuration:"
    echo "---------------------"
    echo "  Server User: ${SERVER_USER}"
    echo "  Server Host: ${SERVER_HOST}"
    echo "  Server Port: ${SERVER_PORT}"
    echo "  Environment: ${ENVIRONMENT}"
    echo "  Remote Directory: ${PROJECT_ROOT_DIR}"
    echo "  Docker Directory: ${DOCKER_DIR}"
    echo ""
    
    if get_yes_no "Are these settings correct?"; then
        # Test SSH connection
        echo ""
        echo "Testing SSH connection..."
        if ! check_ssh_connection; then
            print_error "ERROR: SSH connection failed!"
            print_info "Please check your SSH configuration and server status."
            
            if get_yes_no "Do you want to run tools locally?"; then
                export RUN_LOCALLY=true
                print_warning "Running in local mode. Some features will be disabled."
            else
                print_info "Please update your settings."
                configure_settings  # Recursively call this function
                return
            fi
        else
            print_success "SUCCESS: SSH connection successful!"
        fi
        
        press_enter_to_continue
        return
    fi
    
    # Get new settings
    echo "Please enter new settings:"
    SERVER_USER=$(get_string_input "Server User" "${SERVER_USER}")
    SERVER_HOST=$(get_string_input "Server Host" "${SERVER_HOST}")
    SERVER_PORT=$(get_string_input "Server Port" "${SERVER_PORT}")
    ENVIRONMENT=$(get_string_input "Environment (dev, staging, prod)" "${ENVIRONMENT}")
    PROJECT_ROOT_DIR=$(get_string_input "Remote Project Directory" "${PROJECT_ROOT_DIR}")
    
    # Save settings to local_config.sh
    mkdir -p "./utils/config"
    echo "#!/usr/bin/env bash" > "./utils/config/local_config.sh"
    echo "" >> "./utils/config/local_config.sh"
    echo "# Local configuration - UPDATED $(date)" >> "./utils/config/local_config.sh"
    echo "export SERVER_USER=\"${SERVER_USER}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_HOST=\"${SERVER_HOST}\"" >> "./utils/config/local_config.sh"
    echo "export SERVER_PORT=\"${SERVER_PORT}\"" >> "./utils/config/local_config.sh"
    echo "export PROJECT_ROOT_DIR=\"${PROJECT_ROOT_DIR}\"" >> "./utils/config/local_config.sh"
    echo "export ENVIRONMENT=\"${ENVIRONMENT}\"" >> "./utils/config/local_config.sh"
    
    print_success "Settings saved to local_config.sh"
    
    # Re-source the config to apply changes
    source "./utils/config/config.sh"
    press_enter_to_continue
} 