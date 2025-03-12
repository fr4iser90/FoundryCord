#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Environment Files Menu
# =======================================================

# Show environment files menu
show_env_files_menu() {
    show_header
    
    print_section_header "Environment Files Management"
    print_menu_item "1" "Edit Bot .env File"
    print_menu_item "2" "Edit Web .env File"
    print_menu_item "3" "Create New Bot .env File"
    print_menu_item "4" "Create New Web .env File"
    print_menu_item "5" "Download .env Files from Server"
    print_menu_item "6" "Upload .env Files to Server"
    print_menu_item "7" "Generate Template .env Files"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) 
            edit_bot_env
            show_env_files_menu
            ;;
        2) 
            edit_web_env
            show_env_files_menu
            ;;
        3) 
            create_bot_env
            show_env_files_menu
            ;;
        4) 
            create_web_env
            show_env_files_menu
            ;;
        5) 
            download_env_files
            show_env_files_menu
            ;;
        6) 
            upload_env_files
            show_env_files_menu
            ;;
        7) 
            create_project_templates
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

# Edit bot .env file
edit_bot_env() {
    show_header
    print_section_header "Edit Bot .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot edit remote .env files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Download the current .env file
    print_info "Downloading current .env file..."
    
    # Create a temporary file
    local temp_file="./temp_bot_env"
    
    # Check if the file exists on the server
    if run_remote_command "test -f ${DOCKER_DIR}/.env" "true"; then
        # Download the file
        scp "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env" "$temp_file"
        
        if [ $? -ne 0 ]; then
            print_error "Failed to download .env file"
            press_enter_to_continue
            return
        fi
    else
        # Create a new file from template
        print_warning "No .env file found on server. Creating from template..."
        cat > "$temp_file" << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_GUILD_ID=your_guild_id_here

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=homelab
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Security
AES_KEY=your_aes_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
    fi
    
    # Open the file in the editor
    print_info "Opening .env file in editor..."
    ${EDITOR:-nano} "$temp_file"
    
    # Upload the file back to the server
    print_info "Uploading .env file to server..."
    scp "$temp_file" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
    
    if [ $? -eq 0 ]; then
        print_success ".env file uploaded successfully"
    else
        print_error "Failed to upload .env file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
    
    # Ask if services should be restarted
    if get_yes_no "Do you want to restart services to apply changes?"; then
        print_info "Restarting services..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
        print_success "Services restarted"
    fi
    
    press_enter_to_continue
}

# Edit web .env file
edit_web_env() {
    show_header
    print_section_header "Edit Web .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot edit remote .env files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Download the current .env file
    print_info "Downloading current web .env file..."
    
    # Create a temporary file
    local temp_file="./temp_web_env"
    
    # Check if the file exists on the server
    if run_remote_command "test -f ${WEB_DIR}/.env" "true"; then
        # Download the file
        scp "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/.env" "$temp_file"
        
        if [ $? -ne 0 ]; then
            print_error "Failed to download web .env file"
            press_enter_to_continue
            return
        fi
    else
        # Create a new file from template
        print_warning "No web .env file found on server. Creating from template..."
        cat > "$temp_file" << EOF
# Web Application Configuration
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_BOT_TOKEN=your_token_here
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback

# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=homelab_web
DB_HOST=web_db
DB_PORT=5432

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
SESSION_SECRET=your_session_secret_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
PORT=8000
EOF
    fi
    
    # Open the file in the editor
    print_info "Opening web .env file in editor..."
    ${EDITOR:-nano} "$temp_file"
    
    # Upload the file back to the server
    print_info "Uploading web .env file to server..."
    scp "$temp_file" "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/.env"
    
    if [ $? -eq 0 ]; then
        print_success "Web .env file uploaded successfully"
    else
        print_error "Failed to upload web .env file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
    
    # Ask if services should be restarted
    if get_yes_no "Do you want to restart web services to apply changes?"; then
        print_info "Restarting web services..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose restart web"
        print_success "Web services restarted"
    fi
    
    press_enter_to_continue
}

# Create new bot .env file
create_bot_env() {
    show_header
    print_section_header "Create New Bot .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot create remote .env files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Create a temporary file
    local temp_file="./temp_bot_env"
    
    # Create the file with template content
    cat > "$temp_file" << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_GUILD_ID=your_guild_id_here

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=homelab
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Security
# Generate with: python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
AES_KEY=$(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())' 2>/dev/null || echo "your_aes_key_here")
# Generate with: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
ENCRYPTION_KEY=$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())' 2>/dev/null || echo "your_encryption_key_here")

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
    
    # Open the file in the editor
    print_info "Opening new .env file in editor..."
    ${EDITOR:-nano} "$temp_file"
    
    # Warn about overwriting existing file
    if run_remote_command "test -f ${DOCKER_DIR}/.env" "true"; then
        if ! get_confirmed_input "This will overwrite the existing .env file. Are you sure?" "yes"; then
            print_info "Operation cancelled"
            rm "$temp_file"
            press_enter_to_continue
            return
        fi
    fi
    
    # Upload the file to the server
    print_info "Uploading .env file to server..."
    run_remote_command "mkdir -p ${DOCKER_DIR}"
    scp "$temp_file" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
    
    if [ $? -eq 0 ]; then
        print_success "New .env file uploaded successfully"
    else
        print_error "Failed to upload .env file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
    
    press_enter_to_continue
}

# Create new web .env file
create_web_env() {
    show_header
    print_section_header "Create New Web .env File"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot create remote .env files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Create a temporary file
    local temp_file="./temp_web_env"
    
    # Create the file with template content
    cat > "$temp_file" << EOF
# Web Application Configuration
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_BOT_TOKEN=your_token_here
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback

# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=homelab_web
DB_HOST=web_db
DB_PORT=5432

# Security
JWT_SECRET_KEY=$(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())' 2>/dev/null || echo "your_jwt_secret_key_here")
SESSION_SECRET=$(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())' 2>/dev/null || echo "your_session_secret_here")

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
PORT=8000
EOF
    
    # Open the file in the editor
    print_info "Opening new web .env file in editor..."
    ${EDITOR:-nano} "$temp_file"
    
    # Warn about overwriting existing file
    if run_remote_command "test -f ${WEB_DIR}/.env" "true"; then
        if ! get_confirmed_input "This will overwrite the existing web .env file. Are you sure?" "yes"; then
            print_info "Operation cancelled"
            rm "$temp_file"
            press_enter_to_continue
            return
        fi
    fi
    
    # Upload the file to the server
    print_info "Uploading web .env file to server..."
    run_remote_command "mkdir -p ${WEB_DIR}"
    scp "$temp_file" "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/.env"
    
    if [ $? -eq 0 ]; then
        print_success "New web .env file uploaded successfully"
    else
        print_error "Failed to upload web .env file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
    
    press_enter_to_continue
}

# Download .env files from server
download_env_files() {
    show_header
    print_section_header "Download .env Files"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot download files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Create local .env directory if it doesn't exist
    mkdir -p "./env-files"
    
    # Get timestamp for unique filenames
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Download bot .env file
    if run_remote_command "test -f ${DOCKER_DIR}/.env" "true"; then
        print_info "Downloading bot .env file..."
        scp "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env" "./env-files/bot_env_${timestamp}"
        
        if [ $? -eq 0 ]; then
            print_success "Bot .env file downloaded to ./env-files/bot_env_${timestamp}"
        else
            print_error "Failed to download bot .env file"
        fi
    else
        print_warning "No bot .env file found on server"
    fi
    
    # Download web .env file
    if run_remote_command "test -f ${WEB_DIR}/.env" "true"; then
        print_info "Downloading web .env file..."
        scp "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/.env" "./env-files/web_env_${timestamp}"
        
        if [ $? -eq 0 ]; then
            print_success "Web .env file downloaded to ./env-files/web_env_${timestamp}"
        else
            print_error "Failed to download web .env file"
        fi
    else
        print_warning "No web .env file found on server"
    fi
    
    press_enter_to_continue
}

# Upload .env files to server
upload_env_files() {
    show_header
    print_section_header "Upload .env Files"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot upload files in local mode"
        press_enter_to_continue
        return
    fi
    
    # Check if env-files directory exists
    if [ ! -d "./env-files" ]; then
        print_error "No env-files directory found"
        print_info "Create a directory named 'env-files' and place your .env files there"
        press_enter_to_continue
        return
    fi
    
    # List available files
    print_info "Available .env files:"
    ls -la ./env-files/
    
    # Ask which files to upload
    read -p "Enter the name of the bot .env file to upload (or press enter to skip): " bot_env_file
    read -p "Enter the name of the web .env file to upload (or press enter to skip): " web_env_file
    
    # Upload bot .env file
    if [ -n "$bot_env_file" ]; then
        if [ -f "./env-files/$bot_env_file" ]; then
            print_info "Uploading bot .env file..."
            run_remote_command "mkdir -p ${DOCKER_DIR}"
            scp "./env-files/$bot_env_file" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
            
            if [ $? -eq 0 ]; then
                print_success "Bot .env file uploaded successfully"
            else
                print_error "Failed to upload bot .env file"
            fi
        else
            print_error "Bot .env file not found: ./env-files/$bot_env_file"
        fi
    fi
    
    # Upload web .env file
    if [ -n "$web_env_file" ]; then
        if [ -f "./env-files/$web_env_file" ]; then
            print_info "Uploading web .env file..."
            run_remote_command "mkdir -p ${WEB_DIR}"
            scp "./env-files/$web_env_file" "${SERVER_USER}@${SERVER_HOST}:${WEB_DIR}/.env"
            
            if [ $? -eq 0 ]; then
                print_success "Web .env file uploaded successfully"
            else
                print_error "Failed to upload web .env file"
            fi
        else
            print_error "Web .env file not found: ./env-files/$web_env_file"
        fi
    fi
    
    # Ask if services should be restarted
    if get_yes_no "Do you want to restart services to apply changes?"; then
        print_info "Restarting services..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
        print_success "Services restarted"
    fi
    
    press_enter_to_continue
} 