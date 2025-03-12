#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Main Menu
# =======================================================

# Show main menu
show_main_menu() {
    show_header
    
    print_section_header "Main Menu"
    print_menu_item "1" "Deployment Tools"
    print_menu_item "2" "Container Management"
    print_menu_item "3" "Testing Tools"
    print_menu_item "4" "Database Tools"
    print_menu_item "5" "Development Tools"
    print_menu_item "6" "Configure Settings"
    print_menu_item "7" "Manage Environment Files"
    print_menu_item "8" "View Logs"
    print_exit_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) show_deployment_menu ;;
        2) show_container_menu ;;
        3) show_testing_menu ;;
        4) show_database_menu ;;
        5) show_development_menu ;;
        6) configure_settings; show_main_menu ;;
        7) show_env_files_menu ;;
        8) show_logs_menu ;;
        0) exit 0 ;;
        *) 
            print_error "Invalid option!"
            sleep 1
            show_main_menu
            ;;
    esac
}

# Validate configuration
validate_config() {
    show_header
    
    echo "Current configuration:"
    echo "---------------------"
    echo -e "  Server User: ${GREEN}${SERVER_USER}${NC}"
    echo -e "  Server Host: ${GREEN}${SERVER_HOST}${NC}"
    echo -e "  Server Port: ${GREEN}${SERVER_PORT}${NC}"
    echo -e "  Environment: ${GREEN}${ENVIRONMENT:-dev}${NC}"
    echo -e "  Remote Directory: ${GREEN}${PROJECT_ROOT_DIR}${NC}"
    echo -e "  Docker Directory: ${GREEN}${DOCKER_DIR}${NC}"
    echo ""
    
    if ! get_yes_no "Are these settings correct?" "y"; then
        configure_settings
    fi
    
    # Check SSH connection
    echo -e "\nTesting SSH connection..."
    if check_ssh_connection; then
        print_success "SSH connection successful!"
    else
        print_error "SSH connection failed!"
        echo "Please check your SSH configuration and server status."
        
        if get_yes_no "Do you want to run tools locally?"; then
            export RUN_LOCALLY=true
            print_warning "Running in local mode. Some features will be limited."
        else
            echo "Returning to configuration..."
            configure_settings
        fi
    fi
    
    press_enter_to_continue
}

# Configure settings
configure_settings() {
    show_header
    print_section_header "Configure Settings"
    
    SERVER_USER=$(get_string_input "Server User" "${SERVER_USER}")
    SERVER_HOST=$(get_string_input "Server Host" "${SERVER_HOST}")
    SERVER_PORT=$(get_string_input "Server Port" "${SERVER_PORT}")
    PROJECT_ROOT_DIR=$(get_string_input "Remote Project Directory" "${PROJECT_ROOT_DIR}")
    ENVIRONMENT=$(get_string_input "Environment (dev/staging/prod)" "${ENVIRONMENT:-dev}")
    
    # Save to local config
    echo "#!/usr/bin/env bash" > "./utils/config/local_config.sh"
    echo "" >> "./utils/config/local_config.sh"
    echo "# Local configuration overrides" >> "./utils/config/local_config.sh"
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