#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Check Services
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Main Function
# ------------------------------------------------------
check_services() {
    log_info "Checking services status..."
    
    if [ "$RUN_LOCALLY" = true ]; then
        # Check local services (placeholder)
        print_success "Local service check: simulated in local mode"
        return 0
    else
        # Check remote services
        local services_status
        services_status=$(run_remote_command "cd ${DOCKER_DIR} && docker compose ps --services --filter \"status=running\"" "silent")
        
        if [ -z "$services_status" ]; then
            log_warning "No services are currently running"
            return 1
        else
            log_success "Running services: ${services_status//$'\n'/, }"
            return 0
        fi
    fi
}

# ------------------------------------------------------
# Main Execution
# ------------------------------------------------------
check_services
exit $? 