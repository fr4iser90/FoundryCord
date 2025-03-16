#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Update Docker
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Main Function
# ------------------------------------------------------
update_docker() {
    log_info "Updating Docker services..."
    
    if [ "$RUN_LOCALLY" = true ]; then
        # Local update (placeholder)
        print_success "Local Docker update: simulated in local mode"
        return 0
    else
        # Remote update
        run_remote_command "cd ${DOCKER_DIR} && docker compose down && docker compose up -d"
        
        if [ $? -eq 0 ]; then
            log_success "Docker services updated successfully"
            return 0
        else
            log_error "Failed to update Docker services"
            return 1
        fi
    fi
}

# ------------------------------------------------------
# Main Execution
# ------------------------------------------------------
update_docker
exit $? 