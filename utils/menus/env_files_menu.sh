#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Environment Files Menu
# =======================================================

# Show environment files menu
show_env_files_menu() {
    show_header
    print_section_header "Environment Files Management"
    
    # Enhanced menu with sync option
    print_menu_item "1" "Edit .env File"
    print_menu_item "2" "Upload .env File to Server"
    print_menu_item "3" "Download .env File from Server"
    print_menu_item "4" "Generate Template .env File"
    print_menu_item "5" "Sync Environment Values from Docker"
    
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case $choice in
        1)
            edit_env_file
            press_enter_to_continue
            show_env_files_menu
            ;;
        2)
            upload_env_file
            press_enter_to_continue
            show_env_files_menu
            ;;
        3)
            download_env_file
            press_enter_to_continue
            show_env_files_menu
            ;;
        4)
            generate_template_env
            press_enter_to_continue
            show_env_files_menu
            ;;
        5)
            sync_env_values
            press_enter_to_continue
            show_env_files_menu
            ;;
        0)
            show_main_menu
            ;;
        *)
            print_error "Invalid option!"
            sleep 1
            show_env_files_menu
            ;;
    esac
}

# Edit .env file
edit_env_file() {
    clear
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot edit .env file in local mode"
        press_enter_to_continue
        return
    fi
    
    local env_path="${PROJECT_ROOT_DIR}/.env"
    
    print_section_header "Edit .env File"
    
    # Check if .env file exists in project root
    if ! run_remote_command "test -f ${env_path}" "silent"; then
        # If not in root, check Docker directory
        env_path="${DOCKER_DIR}/.env"
        if ! run_remote_command "test -f ${env_path}" "silent"; then
            print_error ".env file not found on server"
            if get_yes_no "Would you like to create a new .env file?"; then
                generate_template_env
                return
            else
                press_enter_to_continue
                return
            fi
        fi
        print_info "Found .env file in Docker directory"
    }
    
    # Download .env file to a temporary file
    local temp_env_file="/tmp/homelab_env"
    print_info "Downloading .env file..."
    scp "${SERVER_USER}@${SERVER_HOST}:${env_path}" "$temp_env_file"
    
    # Open the file in the user's preferred editor
    local editor="${EDITOR:-nano}"
    if command -v "$editor" > /dev/null; then
        print_info "Opening .env file in $editor..."
        "$editor" "$temp_env_file"
    else
        print_error "Could not find editor: $editor"
        print_info "Trying alternatives: nano, vim, vi..."
        
        for alt_editor in nano vim vi; do
            if command -v "$alt_editor" > /dev/null; then
                print_info "Opening .env file in $alt_editor..."
                "$alt_editor" "$temp_env_file"
                break
            fi
        done
    fi
    
    # Upload the edited file back to the server
    if get_yes_no "Save changes to .env file?"; then
        print_info "Uploading changes..."
        # Upload to project root
        scp "$temp_env_file" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/.env"
        
        # Also copy to docker directory for compatibility
        if run_remote_command "test -d ${DOCKER_DIR}" "silent"; then
            print_info "Copying to Docker directory for compatibility..."
            run_remote_command "cp ${PROJECT_ROOT_DIR}/.env ${DOCKER_DIR}/.env"
        fi
        
        print_success "Changes saved successfully!"
        
        # Ask if services should be restarted
        if get_yes_no "Do you want to restart services to apply changes?"; then
            print_info "Restarting services..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
            print_success "Services restarted"
        fi
    } else {
        print_info "Changes discarded."
    }
    
    # Clean up
    rm -f "$temp_env_file"
    press_enter_to_continue
}

# Upload a local .env file to server
upload_env_file() {
    clear
    print_section_header "Upload .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot upload files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Look for .env in common locations
    local local_env_file=""
    
    if [ -f "./.env" ]; then
        local_env_file="./.env"
    elif [ -f "${LOCAL_GIT_DIR}/.env" ]; then
        local_env_file="${LOCAL_GIT_DIR}/.env"
    else
        print_error "No .env file found in current directory or git root"
        print_info "Please specify the path to your .env file:"
        read -p "> " local_env_file
        
        if [ ! -f "$local_env_file" ]; then
            print_error "File not found: $local_env_file"
            press_enter_to_continue
            return
        fi
    fi
    
    print_info "Using .env file: $local_env_file"
    
    # Upload the file to both project root and docker directory
    print_info "Uploading .env file to server..."
    scp "$local_env_file" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/.env"
    
    if run_remote_command "test -d ${DOCKER_DIR}" "silent"; then
        print_info "Copying to Docker directory for compatibility..."
        run_remote_command "cp ${PROJECT_ROOT_DIR}/.env ${DOCKER_DIR}/.env"
    fi
    
    print_success ".env file uploaded successfully!"
    
    # Ask if services should be restarted
    if get_yes_no "Do you want to restart services to apply changes?"; then
        print_info "Restarting services..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
        print_success "Services restarted"
    fi
    
    press_enter_to_continue
}

# Download .env file from server
download_env_file() {
    clear
    print_section_header "Download .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot download files in local mode"
        press_enter_to_continue
        return
    fi
    
    local env_path="${PROJECT_ROOT_DIR}/.env"
    
    # Check if .env file exists in project root
    if ! run_remote_command "test -f ${env_path}" "silent"; then
        # If not in root, check Docker directory
        env_path="${DOCKER_DIR}/.env"
        if ! run_remote_command "test -f ${env_path}" "silent"; then
            print_error ".env file not found on server"
            press_enter_to_continue
            return
        fi
        print_info "Found .env file in Docker directory"
    }
    
    # Get timestamp for unique filename
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local output_file="./env_backup_${timestamp}"
    
    # Download the file
    print_info "Downloading .env file..."
    scp "${SERVER_USER}@${SERVER_HOST}:${env_path}" "$output_file"
    
    if [ $? -eq 0 ]; then
        print_success ".env file downloaded to $output_file"
    else
        print_error "Failed to download .env file"
    fi
    
    press_enter_to_continue
}

# Generate template .env file
generate_template_env() {
    clear
    print_section_header "Generate Template .env File"
    
    print_info "Creating a basic .env file with essential variables..."
    
    # Get user input for essential variables
    local DISCORD_BOT_TOKEN=$(get_string_input "Discord Bot Token" "")
    local DISCORD_BOT_ID=$(get_string_input "Discord Client ID" "")
    local DISCORD_BOT_SECRET=$(get_string_input "Discord Client Secret" "")
    local postgres_password=$(get_string_input "PostgreSQL Password" "postgres")
    local jwt_secret=$(get_string_input "JWT Secret Key (for web)" "$(openssl rand -hex 32)")
    
    # Create .env file content
    local env_content="# HomeLab Discord Bot Environment Configuration
# Generated on $(date)

# Discord Configuration
DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
DISCORD_BOT_ID=${DISCORD_BOT_ID}
DISCORD_BOT_SECRET=${DISCORD_BOT_SECRET}

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=homelab
POSTGRES_HOST=homelab-postgres
POSTGRES_PORT=5432

# Web Configuration
JWT_SECRET_KEY=${jwt_secret}
WEB_HOST=0.0.0.0
WEB_PORT=8000
ENVIRONMENT=${ENVIRONMENT:-dev}

# Redis Configuration
REDIS_HOST=homelab-redis
REDIS_PORT=6379
"
    
    if [ "$RUN_LOCALLY" = false ]; then
        # Save the .env file to a temporary local file
        local temp_env_file="/tmp/homelab_temp_env"
        echo "$env_content" > "$temp_env_file"
        
        # Upload to both the project root and docker directory
        print_info "Uploading .env file to server..."
        scp "$temp_env_file" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/.env"
        
        if run_remote_command "test -d ${DOCKER_DIR}" "silent"; then
            print_info "Copying to Docker directory for compatibility..."
            run_remote_command "cp ${PROJECT_ROOT_DIR}/.env ${DOCKER_DIR}/.env"
        fi
        
        # Remove temporary file
        rm "$temp_env_file"
        
        print_success ".env file created and uploaded successfully!"
        
        # Ask if services should be restarted
        if get_yes_no "Do you want to restart services to apply the new .env?"; then
            print_info "Restarting services..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
            print_success "Services restarted"
        fi
    else
        # In local mode, just save to current directory
        echo "$env_content" > "./.env"
        print_success ".env file created in current directory"
    fi
    
    press_enter_to_continue
}

# Sync environment values between docker/.env and local environment
sync_env_values() {
    print_section_header "Sync Environment Values"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot sync environment values in local mode"
        return 1
    fi
    
    # Check if docker/.env exists on the server
    if ! run_remote_command "test -f ${DOCKER_DIR}/.env" "silent"; then
        print_error "No .env file found in Docker directory"
        return 1
    fi
    
    print_info "Loading environment values from Docker .env file..."
    
    # Create a temporary file to store the .env content
    local temp_env_file="/tmp/docker_env_$$"
    scp "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env" "$temp_env_file"
    
    # Export values to current environment
    export $(grep -v '^#' "$temp_env_file" | xargs)
    
    print_success "Environment values synced successfully!"
    print_info "These values will be available for this session only."
    
    # Ask if the user wants to apply these values to local environment
    if get_yes_no "Would you like to save these values to local environment?"; then
        # Save to local .env file
        cp "$temp_env_file" "./docker/.env"
        print_success "Values saved to ./docker/.env"
    fi
    
    # Cleanup
    rm "$temp_env_file"
    
    return 0
} 