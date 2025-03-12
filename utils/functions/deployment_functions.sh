#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Functions
# =======================================================

# Run quick deploy (wrapper for quick_deploy.sh) - SAFE, preserves database
run_quick_deploy() {
    clear
    print_section_header "Quick Deploy (Database Safe)"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot deploy in local mode"
        return 1
    fi
    
    print_info "Running quick deploy (preserves database)..."
    ./utils/deployment/quick_deploy.sh
    return $?
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
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot deploy in local mode"
        return 1
    fi
    
    print_error "Performing COMPLETE RESET with DATABASE DELETION..."
    print_error "ALL DATA WILL BE LOST!"
    
    # Full deployment with -v flag to remove volumes (DESTROYS DATABASE)
    run_remote_command "cd ${DOCKER_DIR} && docker compose down -v && docker compose build --no-cache && docker compose up -d"
    
    print_success "Full reset deployment completed."
    print_warning "Your database has been reset to default state."
    
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