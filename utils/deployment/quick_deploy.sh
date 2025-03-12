#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Quick Deploy Script
# =======================================================
# This script provides quick deployment with direct .env file copying

# Source configuration
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../config/config.sh"
source "${SCRIPT_DIR}/../lib/common.sh"

# Default settings
REBUILD=false
REMOVE_VOLUMES=false

# ------------------------------------------------------
# Parse command line arguments
# ------------------------------------------------------
parse_arguments() {
    for arg in "$@"; do
        case $arg in
            --rebuild)
                REBUILD=true
                ;;
            --remove-volumes|--remove-V)
                REMOVE_VOLUMES=true
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_warning "Unknown argument: $arg"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done

    # If removing volumes, we must rebuild
    if [ "$REMOVE_VOLUMES" = "true" ]; then
        REBUILD=true
    fi
}

# ------------------------------------------------------
# Show help information
# ------------------------------------------------------
show_help() {
    echo "HomeLab Discord Bot - Quick Deploy Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --rebuild        Force rebuild of containers"
    echo "  --remove-volumes Remove volumes during down (will delete database)"
    echo "  --remove-V       Short alias for --remove-volumes"
    echo "  --help           Show this help message"
}

# ------------------------------------------------------
# Deploy the bot application
# ------------------------------------------------------
deploy_bot() {
    log_info "Starting deployment to ${SERVER_HOST}..."
    
    # 1. Check SSH connection
    if ! check_ssh_connection; then
        log_error "SSH connection failed. Aborting deployment."
        exit 1
    fi
    
    # 2. Create necessary directories
    log_info "Creating necessary directories..."
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/app/bot"
    run_remote_command "mkdir -p ${BOT_DOCKER_DIR}"
    
    # 3. DIRECTLY COPY .ENV FILE - NO CHECKS
    log_info "Copying .env file to server..."
    scp "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/docker/bot/.env" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/.env"
    log_success ".env file copied to server."
    
    # 4. Copy bot code
    log_info "Copying bot code to server..."
    scp -r "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/app/bot/"* "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/app/bot/"
    log_success "Bot code copied successfully."
    
    # 5. Copy Docker files
    log_info "Copying Docker files to server..."
    scp "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/docker/bot/docker-compose.yml" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    scp "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/docker/bot/Dockerfile" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    scp "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/docker/bot/entrypoint.sh" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    scp "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/docker/bot/init-db.sh" "${SERVER_USER}@${SERVER_HOST}:${BOT_DOCKER_DIR}/"
    log_success "Docker files copied successfully."
    
    # 6. Copy utility scripts
    log_info "Copying utility scripts..."
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/utils"
    scp -r "${SSH_OPTS[@]}" "${LOCAL_GIT_DIR}/utils/"* "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/utils/"
    log_success "Utility scripts copied successfully."
    
    # 7. Make scripts executable
    log_info "Making scripts executable..."
    run_remote_command "find ${PROJECT_ROOT_DIR}/utils -name \"*.sh\" -type f -exec chmod +x {} \\;"
    log_success "Scripts are now executable."
    
    # 8. Deploy the bot (rebuild if requested)
    log_info "Deploying the bot..."
    
    if [ "$REBUILD" = "true" ]; then
        log_warning "Performing full rebuild..."
        
        if [ "$REMOVE_VOLUMES" = "true" ]; then
            log_warning "⚠️ REMOVING VOLUMES - ALL DATA WILL BE DELETED ⚠️"
            run_remote_command "cd ${BOT_DOCKER_DIR} && docker compose down -v"
        else
            run_remote_command "cd ${BOT_DOCKER_DIR} && docker compose down"
        fi
        
        run_remote_command "cd ${BOT_DOCKER_DIR} && docker compose build --no-cache && docker compose up -d"
    else
        log_info "Updating existing containers..."
        run_remote_command "cd ${BOT_DOCKER_DIR} && docker compose up -d --build"
    fi
    
    log_success "Deployment completed successfully!"
    
    # 9. Check if services are running
    check_services
}

# ------------------------------------------------------
# Check if services are running
# ------------------------------------------------------
check_services() {
    log_info "Checking if services are running..."
    sleep 10  # Give services a moment to start
    
    local all_running=true
    
    if run_remote_command "docker ps | grep -q ${BOT_CONTAINER}" "true"; then
        log_success "✓ ${BOT_CONTAINER} is running."
    else
        log_error "✗ ${BOT_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if run_remote_command "docker ps | grep -q ${POSTGRES_CONTAINER}" "true"; then
        log_success "✓ ${POSTGRES_CONTAINER} is running."
    else
        log_error "✗ ${POSTGRES_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if run_remote_command "docker ps | grep -q ${REDIS_CONTAINER}" "true"; then
        log_success "✓ ${REDIS_CONTAINER} is running."
    else
        log_error "✗ ${REDIS_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if [ "$all_running" = "false" ]; then
        log_warning "Some services are not running! Check logs with:"
        echo "ssh ${SERVER_USER}@${SERVER_HOST} \"cd ${BOT_DOCKER_DIR} && docker compose logs\""
    fi
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Setup SSH options array
    SSH_OPTS=(-i "$SERVER_KEY" -p "$SERVER_PORT")
    
    # Deploy the bot
    deploy_bot
}

# Run the main function
main "$@" 