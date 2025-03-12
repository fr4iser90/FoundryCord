#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Script
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Command-line Arguments Parsing
# ------------------------------------------------------
parse_args "$@"

# ------------------------------------------------------
# Main Deployment Function
# ------------------------------------------------------
deploy_changes() {
    log_section "Deploying changes to ${SERVER_HOST}"
    
    # Create a temporary directory
    TMP_DIR=$(mktemp -d)
    log_info "Created temporary directory: ${TMP_DIR}"
    
    # Copy essential files to deploy
    cp compose/docker-compose.yml "${TMP_DIR}/"
    cp compose/Dockerfile "${TMP_DIR}/"
    cp -r utils "${TMP_DIR}/"
    cp app/bot/requirements.txt "${TMP_DIR}/"
    
    # Upload Docker Compose files
    log_info "Uploading Docker Compose files..."
    run_remote_command "mkdir -p ${DOCKER_DIR}"
    upload_file "${TMP_DIR}/docker-compose.yml" "${DOCKER_DIR}/docker-compose.yml"
    upload_file "${TMP_DIR}/Dockerfile" "${DOCKER_DIR}/Dockerfile"
    
    # Upload utilities
    log_info "Uploading utility scripts..."
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/utils"
    for util_file in $(find "${TMP_DIR}/utils" -type f -name "*.sh"); do
        rel_path="${util_file#$TMP_DIR/utils/}"
        remote_path="${PROJECT_ROOT_DIR}/utils/${rel_path}"
        remote_dir=$(dirname "$remote_path")
        
        # Ensure remote directory exists
        run_remote_command "mkdir -p $remote_dir" "true"
        
        # Upload the file and make it executable
        upload_file "$util_file" "$remote_path"
        run_remote_command "chmod +x $remote_path" "true"
    done
    
    # Upload requirements
    log_info "Uploading requirements file..."
    run_remote_command "mkdir -p ${BOT_DIR}"
    upload_file "${TMP_DIR}/requirements.txt" "${BOT_DIR}/requirements.txt"
    
    # Clean up
    rm -rf "${TMP_DIR}"
    
    # Optionally rebuild Docker containers
    if [ "$REBUILD_ON_DEPLOY" = "true" ]; then
        log_section "Performing Docker rebuild"
        run_remote_command "cd ${DOCKER_DIR} && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
        
        log_info "Waiting for services to start..."
        sleep 15
        
        log_success "Deployment and rebuild completed successfully."
    else
        log_success "Deployment completed successfully."
    fi
    
    return 0
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    # Check SSH connection
    check_ssh_connection
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Deploy changes
    deploy_changes
    if [ $? -ne 0 ]; then
        exit 1
    fi
}

# Run the main function
main 