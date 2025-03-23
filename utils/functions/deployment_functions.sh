#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Functions
# =======================================================

# Deploy application files to remote server or local directory
deploy_app() {
    print_section_header "Deploying App Files"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_info "Deploying app files to local directory..."
        
        # Ensure local directories exist
        mkdir -p "${LOCAL_APP_DIR}"
        
        # Copy application files
        cp -r "${LOCAL_GIT_DIR}/app/"* "${LOCAL_APP_DIR}/"
        
        if [ $? -eq 0 ]; then
            print_success "Application files deployed locally to ${LOCAL_APP_DIR}!"
        else
            print_error "Failed to copy application files locally"
            return 1
        fi
    else
        # Copy application files to remote server
        print_info "Copying application files to remote server..."
        scp -r "${LOCAL_GIT_DIR}/app/"* "${SERVER_USER}@${SERVER_HOST}:${APP_DIR}/"
        
        if [ $? -eq 0 ]; then
            print_success "Application files deployed successfully to remote server!"
        else
            print_error "Failed to copy application files to remote server"
            return 1
        fi
    fi
    
    return 0
}

# Deploy Docker configuration files to remote server or local directory
deploy_docker() {
    print_section_header "Deploying Docker Configuration"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_info "Deploying Docker configuration to local directory..."
        
        # Ensure local docker directory exists
        mkdir -p "${LOCAL_DOCKER_DIR}"
        
        # Copy Docker files
        cp -r "${LOCAL_GIT_DIR}/docker/"* "${LOCAL_DOCKER_DIR}/"
        
        # Copy .env files (explicitly to make sure they're included)
        if [ -f "${LOCAL_GIT_DIR}/docker/.env" ]; then
            cp "${LOCAL_GIT_DIR}/docker/.env" "${LOCAL_DOCKER_DIR}/.env"
            print_success "Copied .env file from ${LOCAL_GIT_DIR}/docker/.env"
        elif [ -f "${LOCAL_GIT_DIR}/.env" ]; then
            cp "${LOCAL_GIT_DIR}/.env" "${LOCAL_DOCKER_DIR}/.env"
            print_success "Copied .env file from ${LOCAL_GIT_DIR}/.env"
        elif [ -f "${LOCAL_GIT_DIR}/docker/.env.example" ]; then
            print_warning "No .env file found, copying .env.example. You'll need to edit this!"
            cp "${LOCAL_GIT_DIR}/docker/.env.example" "${LOCAL_DOCKER_DIR}/.env"
        else
            print_error "No .env or .env.example file found! Deployment may fail."
        fi
        
        if [ $? -eq 0 ]; then
            print_success "Docker configuration files deployed locally to ${LOCAL_DOCKER_DIR}!"
        else
            print_error "Failed to copy Docker configuration files locally"
            return 1
        fi
    else
        # Copy Docker files to remote server
        print_info "Copying Docker configuration files..."
        scp -r "${LOCAL_GIT_DIR}/docker/"* "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/"
        
        # Copy .env files (explicitly to make sure they're included)
        print_info "Copying environment files..."
        if [ -f "${LOCAL_GIT_DIR}/docker/.env" ]; then
            scp "${LOCAL_GIT_DIR}/docker/.env" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
            print_success "Copied .env file from ${LOCAL_GIT_DIR}/docker/.env"
        elif [ -f "${LOCAL_GIT_DIR}/.env" ]; then
            scp "${LOCAL_GIT_DIR}/.env" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
            print_success "Copied .env file from ${LOCAL_GIT_DIR}/.env"
        elif [ -f "${LOCAL_GIT_DIR}/docker/.env.example" ]; then
            print_warning "No .env file found, copying .env.example. You'll need to edit this!"
            scp "${LOCAL_GIT_DIR}/docker/.env.example" "${SERVER_USER}@${SERVER_HOST}:${DOCKER_DIR}/.env"
        else
            print_error "No .env or .env.example file found! Deployment may fail."
        fi
        
        if [ $? -eq 0 ]; then
            print_success "Docker configuration files deployed successfully!"
        else
            print_error "Failed to copy Docker configuration files"
            return 1
        fi
    fi
    
    return 0
}

# Deploy containers (restart/rebuild)
deploy_containers() {
    print_section_header "Deploying Containers"
    
    if [ "$RUN_LOCALLY" = true ]; then
        # Verify .env file exists locally before deploying
        if [ ! -f "${LOCAL_DOCKER_DIR}/.env" ]; then
            print_error "No .env file found locally! Container deployment will fail."
            print_info "Please ensure .env file exists at ${LOCAL_DOCKER_DIR}/.env"
            
            # Ask if user wants to continue anyway
            if ! get_yes_no "Continue without .env file?"; then
                print_info "Deployment cancelled."
                return 1
            fi
        fi
        
        # Start containers locally
        print_info "Starting containers in local Docker environment..."
        cd "${LOCAL_DOCKER_DIR}" || { print_error "Local Docker directory not found!"; return 1; }
        
        if [ "${AUTO_BUILD_ENABLED}" = "true" ]; then
            print_info "Building containers (this may take a while)..."
            docker compose build
        fi
        
        print_info "Starting Docker containers locally..."
        docker compose up -d
        
        if [ $? -eq 0 ]; then
            print_success "Containers started locally!"
        else
            print_error "Failed to start containers locally"
            return 1
        fi
    else
        # Verify .env file exists on server before deploying
        if ! run_remote_command "test -f ${DOCKER_DIR}/.env" "true"; then
            print_error "No .env file found on server! Container deployment will fail."
            print_info "Please ensure .env file exists at ${DOCKER_DIR}/.env"
            
            # Ask if user wants to continue anyway
            if ! get_yes_no "Continue without .env file?"; then
                print_info "Deployment cancelled."
                return 1
            fi
        fi
        
        # Start containers
        print_info "Starting containers on remote server..."
        
        if [ "${AUTO_BUILD_ENABLED}" = "true" ]; then
            print_info "Building containers (this may take a while)..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose build"
        fi
        
        print_info "Starting Docker containers..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose up -d"
        
        if [ $? -eq 0 ]; then
            print_success "Containers started successfully!"
        else
            print_error "Failed to start containers"
            return 1
        fi
    fi
    
    return 0
}

# Check if services are running (similar to check_services.sh)
check_deployed_services() {
    print_section_header "Checking Deployed Services"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot check services in local mode"
        return 1
    fi
    
    print_info "Waiting for services to start..."
    sleep 5  # Give services time to start
    
    local all_running=true
    
    if run_remote_command "docker ps | grep -q ${BOT_CONTAINER}" "true"; then
        print_success "✓ ${BOT_CONTAINER} is running."
    else
        print_error "✗ ${BOT_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if run_remote_command "docker ps | grep -q ${POSTGRES_CONTAINER}" "true"; then
        print_success "✓ ${POSTGRES_CONTAINER} is running."
    else
        print_error "✗ ${POSTGRES_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if run_remote_command "docker ps | grep -q ${REDIS_CONTAINER}" "true"; then
        print_success "✓ ${REDIS_CONTAINER} is running."
    else
        print_error "✗ ${REDIS_CONTAINER} is NOT running!"
        all_running=false
    fi
    
    if [ "$all_running" = "false" ]; then
        print_warning "Some services are not running! Check logs with:"
        echo "ssh ${SERVER_USER}@${SERVER_HOST} \"cd ${DOCKER_DIR} && docker compose logs\""
        return 1
    fi
    
    return 0
}

# Full deployment function - combines all steps
full_deploy() {
    print_section_header "Full Deployment"
    
    # 1. Deploy application files
    if ! deploy_app; then
        print_error "Deployment failed at app deployment stage"
        return 1
    fi
    
    # 2. Deploy Docker configuration
    if ! deploy_docker; then
        print_error "Deployment failed at Docker configuration stage"
        return 1
    fi
    
    # 3. Deploy containers
    if ! deploy_containers; then
        print_error "Deployment failed at container deployment stage"
        return 1
    fi
    
    # 4. Check services
    check_deployed_services
    
    print_success "Deployment completed successfully!"
    return 0
}

# Run quick deploy (wrapper for quick_deploy.sh) - SAFE, preserves database
run_quick_deploy() {
    print_section_header "Quick Deploy (Database Safe)"
    
    # 1. Deploy app files
    if ! deploy_app; then
        print_error "Deployment failed at app deployment stage"
        return 1
    fi
    
    # 2. Deploy Docker configuration
    if ! deploy_docker; then
        print_error "Deployment failed at Docker configuration stage"
        return 1
    fi
    
    # 3. Deploy containers
    if ! deploy_containers; then
        print_error "Deployment failed at container deployment stage"
        return 1
    fi
    
    # 4. Check services
    if [ "$RUN_LOCALLY" = true ]; then
        print_info "Containers started locally."
        print_info "Check your local Docker Dashboard to verify services are running"
    else
        check_deployed_services
    fi
    
    print_success "Quick deployment completed successfully!"
    return 0
}

# Run partial deploy - SAFE, rebuilds containers only without touching database
run_partial_deploy() {
    clear
    print_section_header "Partial Deploy (Database Safe)"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot deploy in local mode"
        return 1
    fi
    
    print_info "Rebuilding containers without touching database..."
    print_info "This is a SAFE operation that preserves your database."
    
    # Use "stop" instead of "down" to ensure volumes are not touched
    run_remote_command "cd ${DOCKER_DIR} && docker compose stop && docker compose rm -f && docker compose build --no-cache && docker compose up -d"
    
    print_success "Partial deployment completed successfully!"
    return 0
}

# Run full RESET deployment - DANGER, will delete all data
run_full_reset_deploy() {
    clear
    print_section_header "⚠️ FULL RESET DEPLOYMENT - DATA WILL BE LOST ⚠️"
    
    print_error "Performing COMPLETE RESET with DATABASE DELETION..."
    print_error "ALL DATA WILL BE LOST!"
    
    # Check if we should remove volumes
    local volume_flag=""
    if [ "${REMOVE_VOLUMES}" = "true" ]; then
        print_warning "Volume removal flag set - ALL persistent data will be removed!"
        volume_flag="-v"
    fi
    
    # Full deployment with optional -v flag to remove volumes (DESTROYS DATABASE)
    run_remote_command "cd ${DOCKER_DIR} && docker compose down ${volume_flag}"
    run_remote_command "cd ${DOCKER_DIR} && cd ../.. && rm -rf ./app"
    # First make sure .env files are in place
    print_info "Checking and copying environment files..."
    deploy_docker
    
    run_remote_command "cd ${DOCKER_DIR} && docker compose build --no-cache"
    run_remote_command "cd ${DOCKER_DIR} && docker compose up -d"
    print_success "Full reset deployment completed."
    if [ "${REMOVE_VOLUMES}" = "true" ]; then
        print_warning "Your database has been completely removed."
    else
        print_warning "Your database has been reset to default state."
    fi
    
    return 0
}

# Check services (wrapper for check_services.sh)
check_services() {
    clear
    print_section_header "Service Status Check"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot check services in local mode"
        return 1
    fi
    
    ./utils/deployment/check_services.sh
    return $?
}

# Update Docker configuration (wrapper for update_docker.sh)
update_docker_config() {
    clear
    print_section_header "Update Docker Configuration"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot update Docker configuration in local mode"
        return 1
    fi
    
    print_info "This operation is SAFE and preserves your database."
    ./utils/deployment/update_docker.sh
    return $?
}

# Check Docker files (wrapper for check_docker_files.sh)
check_docker_files() {
    clear
    print_section_header "Check Docker Files"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot check Docker files in local mode"
        return 1
    fi
    
    ./utils/deployment/check_docker_files.sh
    return $?
}

# Auto-start services after deployment
auto_start_services() {
    print_section_header "Auto-starting Services"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot auto-start services in local mode"
        return 1
    fi
    
    # Check if auto-start is enabled
    if [ "${AUTO_START}" != "true" ]; then
        print_info "Auto-start is disabled. Skipping service startup."
        return 0
    fi
    
    print_info "Auto-starting services (${AUTO_START_SERVICES})..."
    
    # Start all or specific services
    case "${AUTO_START_SERVICES}" in
        "all")
            run_remote_command "cd ${DOCKER_DIR} && docker compose up -d"
            ;;
        "none")
            print_info "No services selected for auto-start."
            return 0
            ;;
        *)
            # Start only specified services
            for service in ${AUTO_START_SERVICES//,/ }; do
                print_info "Starting ${service} service..."
                run_remote_command "cd ${DOCKER_DIR} && docker compose up -d ${service}"
            done
            ;;
    esac
    
    # Wait if configured to do so
    if [ "${AUTO_START_WAIT}" -gt 0 ]; then
        print_info "Waiting ${AUTO_START_WAIT} seconds for services to initialize..."
        sleep "${AUTO_START_WAIT}"
    fi
    
    # Show service status if feedback is enabled
    if [ "${AUTO_START_FEEDBACK}" != "none" ]; then
        print_info "Checking service status..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose ps"
        
        if [ "${AUTO_START_FEEDBACK}" = "verbose" ]; then
            print_info "Displaying recent logs..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose logs --tail=20"
        fi
    fi
    
    print_success "Auto-start completed successfully!"
    return 0
}

# Save auto-start configuration
save_auto_start_config() {
    local auto_start="$1"
    local auto_start_services="$2"
    local auto_start_feedback="$3"
    
    # Create a temporary file
    local temp_file="/tmp/auto_start_temp.conf"
    echo "$config_content" > "$temp_file"
    
    # Upload the file to the server
    scp "$temp_file" "${SERVER_USER}@${SERVER_HOST}:${PROJECT_ROOT_DIR}/utils/config/auto_start.conf"
    
    # Make it executable
    run_remote_command "chmod +x ${PROJECT_ROOT_DIR}/utils/config/auto_start.conf"
    
    # Remove the temporary file
    rm "$temp_file"
    
    print_success "Auto-start configuration saved!"
}

# Modify quick deploy to use auto-start
run_quick_deploy_with_auto_start() {
    clear
    print_section_header "Quick Deploy with Auto-Start"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot deploy in local mode"
        return 1
    fi
    
    print_info "Running quick deploy with auto-start enabled..."
    
    # 1. Deploy application files
    if ! deploy_app; then
        print_error "Deployment failed at app deployment stage"
        return 1
    fi
    
    # 2. Deploy Docker configuration
    if ! deploy_docker; then
        print_error "Deployment failed at Docker configuration stage"
        return 1
    fi
    
    # 3. Deploy containers with auto-build option
    print_section_header "Building Containers"
    
    if [ "${AUTO_BUILD_ENABLED}" = "true" ]; then
        print_info "Auto-build is enabled. Rebuilding containers..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose down && docker compose build"
    else
        print_info "Auto-build is disabled. Using existing containers..."
    fi
    
    # 4. Auto-start services
    auto_start_services
    
    # 5. Check services
    check_deployed_services
    
    print_success "Deployment with auto-start completed successfully!"
    return 0
}

# Run deployment with real-time monitoring
run_deployment_with_monitoring() {
    clear
    print_section_header "Deployment with Real-time Monitoring"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot deploy in local mode"
        return 1
    fi
    
    print_info "Starting deployment with console feedback..."
    
    # Get services to monitor
    local monitor_services="${1:-all}"
    local show_logs=true
    
    # 1. Deploy application files
    if ! deploy_app; then
        print_error "Deployment failed at app deployment stage"
        return 1
    fi
    
    # 2. Deploy Docker configuration
    if ! deploy_docker; then
        print_error "Deployment failed at Docker configuration stage"
        return 1
    fi
    
    # 3. Deploy containers with specific options for monitoring
    print_section_header "Building and Starting Containers"
    
    if [ "${AUTO_BUILD_ENABLED}" = "true" ]; then
        print_info "Building containers (this may take a while)..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose build"
    fi
    
    # Start containers in background to allow monitoring
    print_info "Starting containers..."
    run_remote_command "cd ${DOCKER_DIR} && docker compose up -d"
    
    if [ "$monitor_services" = "all" ]; then
        # Monitor all logs
        print_info "Monitoring all containers. Press Ctrl+C to stop monitoring..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50"
    else
        # Monitor specific services
        print_info "Monitoring services: ${monitor_services}. Press Ctrl+C to stop monitoring..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50 ${monitor_services//,/ }"
    fi
    
    # 4. Check services after user ends monitoring
    print_info "Monitoring ended. Checking service status..."
    check_deployed_services
    
    print_success "Deployment with monitoring completed successfully!"
    return 0
} 

run_quick_deploy_attach() {
    print_section_header "Quick Deploy (Database Safe)"
    
    # 1. Deploy app files
    if ! deploy_app; then
        print_error "Deployment failed at app deployment stage"
        return 1
    fi
    
    # 2. Deploy Docker configuration
    if ! deploy_docker; then
        print_error "Deployment failed at Docker configuration stage"
        return 1
    fi
    
    # 3. Deploy containers
    if ! deploy_containers; then
        print_error "Deployment failed at container deployment stage"
        return 1
    fi
    
    # 4. Check services
    if [ "$RUN_LOCALLY" = true ]; then
        print_info "Containers started locally."
        print_info "Check your local Docker Dashboard to verify services are running"
    else
        check_deployed_services
    fi
    
    if [ "$RUN_LOCALLY" = true ]; then
        docker attach ${PROJECT_NAME}
    else
        ssh ${SERVER_USER}@${SERVER_HOST} docker attach ${PROJECT_NAME}
    fi   

    print_success "Quick deployment completed successfully!"
    return 0
}
