#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Development Functions
# =======================================================

# Generate encryption keys
generate_encryption_keys() {
    clear
    print_section_header "Generate Encryption Keys"
    
    if command -v nix-shell >/dev/null 2>&1; then
        nix-shell ./utils/development/python-shell.nix
    else
        print_error "nix-shell not installed"
        echo "Please install Nix from https://nixos.org/download.html"
        
        # Fallback to python if available
        if command -v python3 >/dev/null 2>&1; then
            print_warning "Using python3 directly instead..."
            echo "AES_KEY: $(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')"
            
            if python3 -c "import cryptography" >/dev/null 2>&1; then
                echo "ENCRYPTION_KEY: $(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
            else
                print_error "cryptography package not installed. Cannot generate Fernet key."
                echo "Install with: pip install cryptography"
            fi
        else
            print_error "Python 3 not found in path."
        fi
    fi
    
    press_enter_to_continue
    show_development_menu
}

# Initialize development environment
initialize_dev_environment() {
    clear
    print_section_header "Initialize Development Environment"
    
    ./utils/testing/init_test_env.sh
    
    press_enter_to_continue
    show_development_menu
}

# Update utility scripts
update_utility_scripts() {
    clear
    print_section_header "Update Utility Scripts"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot update utility scripts in local mode"
        press_enter_to_continue
        show_development_menu
        return
    else
        print_info "Uploading utility scripts to server..."
        upload_utils_scripts
    fi
    
    press_enter_to_continue
    show_development_menu
}

# Upload utility scripts to server
upload_utils_scripts() {
    # Create remote directory if it doesn't exist
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/utils"
    
    # Upload all utility scripts
    print_info "Uploading utility scripts..."
    scp -r ./utils/* "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/utils/"
    
    if [ $? -eq 0 ]; then
        print_success "Utility scripts uploaded successfully"
        
        # Make scripts executable
        run_remote_command "find ${PROJECT_ROOT_DIR}/utils -name \"*.sh\" -type f -exec chmod +x {} \\;"
        run_remote_command "find ${PROJECT_ROOT_DIR}/utils -name \"*.py\" -type f -exec chmod +x {} \\;"
        
        print_success "Scripts made executable on server"
    else
        print_error "Failed to upload utility scripts"
    fi
}

# Create project templates
create_project_templates() {
    clear
    print_section_header "Create Project Templates"
    
    # Create templates directory if it doesn't exist
    mkdir -p ./templates
    
    # Create bot template
    print_info "Creating Bot template..."
    cat > ./templates/bot.env.template << EOF
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_token_here
DISCORD_BOT_ID=your_client_id_here
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
AES_KEY=your_aes_key_here
# Generate with: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
ENCRYPTION_KEY=your_encryption_key_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development  # development, staging, production
EOF
    
    # Create web template
    print_info "Creating Web template..."
    cat > ./templates/web.env.template << EOF
# Web Application Configuration
DISCORD_BOT_ID=your_client_id_here
DISCORD_BOT_SECRET=your_client_secret_here
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
    
    print_success "Templates created in ./templates/ directory"
    
    press_enter_to_continue
    show_development_menu
} 