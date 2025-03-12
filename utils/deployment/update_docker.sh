#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Docker Update Script
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Command-line Arguments Parsing
# ------------------------------------------------------
FORCE_REBUILD=false

parse_docker_args() {
    for arg in "$@"; do
        case $arg in
            --rebuild)
                FORCE_REBUILD=true
                ;;
            *)
                parse_args "$arg" # Pass to common arg parser
                ;;
        esac
    done
}

parse_docker_args "$@"

# ------------------------------------------------------
# Docker Update Functions
# ------------------------------------------------------
copy_docker_files() {
    log_info "Copying Docker files to remote server..."
    
    # Create a temporary directory
    TMP_DIR=$(mktemp -d)
    log_info "Created temporary directory: ${TMP_DIR}"
    
    # Copy Docker related files
    cp compose/docker-compose.yml "${TMP_DIR}/"
    cp compose/Dockerfile "${TMP_DIR}/"
    
    # Upload Docker Compose files
    run_remote_command "mkdir -p ${DOCKER_DIR}" "true"
    upload_file "${TMP_DIR}/docker-compose.yml" "${DOCKER_DIR}/docker-compose.yml"
    upload_file "${TMP_DIR}/Dockerfile" "${DOCKER_DIR}/Dockerfile"
    
    # Clean up
    rm -rf "${TMP_DIR}"
    
    log_success "Docker files copied successfully."
    return 0
}

rebuild_docker() {
    log_info "Rebuilding Docker containers..."
    
    local rebuild_cmd="cd ${DOCKER_DIR}"
    
    if [ "$FORCE_REBUILD" = "true" ]; then
        log_info "Performing a full rebuild with --no-cache"
        rebuild_cmd="${rebuild_cmd} && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
    else
        rebuild_cmd="${rebuild_cmd} && docker-compose down && docker-compose up -d --build"
    fi
    
    run_remote_command "$rebuild_cmd"
    
    if [ $? -ne 0 ]; then
        log_error "Error rebuilding Docker containers."
        return 1
    fi
    
    log_success "Docker containers rebuilt and restarted successfully."
    return 0
}

wait_for_services() {
    log_info "Waiting for services to start..."
    
    # Calculate end time for timeout
    local start_time=$(date +%s)
    local end_time=$((start_time + WAIT_TIMEOUT))
    local current_time=$start_time
    
    # Wait for services or until timeout
    while [ $current_time -lt $end_time ]; do
        # Check if all services are running
        run_remote_command "docker ps | grep -q $BOT_CONTAINER" "true"
        local bot_running=$?
        
        run_remote_command "docker ps | grep -q $POSTGRES_CONTAINER" "true"
        local postgres_running=$?
        
        run_remote_command "docker ps | grep -q $REDIS_CONTAINER" "true"
        local redis_running=$?
        
        if [ $bot_running -eq 0 ] && [ $postgres_running -eq 0 ] && [ $redis_running -eq 0 ]; then
            log_success "All services are running!"
            return 0
        fi
        
        # Wait a bit before checking again
        sleep 5
        current_time=$(date +%s)
    done
    
    # If we got here, the timeout was reached
    log_warning "Timeout reached waiting for services. Some services may not be running yet."
    return 1
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    log_section "HomeLab Discord Bot - Docker Update"
    
    # Check SSH connection
    check_ssh_connection || exit 1
    
    # Copy Docker files
    copy_docker_files || exit 1
    
    # Rebuild Docker
    rebuild_docker || exit 1
    
    # Wait for services to start
    wait_for_services
    
    log_success "Docker update completed successfully."
}

# Run the main function
main 