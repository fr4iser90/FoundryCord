#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Test Results Synchronizer
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# Print diagnostic information
echo "====================== TEST RESULTS SYNC ======================"
echo "LOCAL_GIT_DIR: $LOCAL_GIT_DIR"
echo "LOCAL_PROJECT_DIR: $LOCAL_PROJECT_DIR"

# Create local test results directory if it doesn't exist
mkdir -p "$LOCAL_GIT_DIR/test-results"
mkdir -p "$LOCAL_PROJECT_DIR/docker/test-results"

# Copy test results from local development directory to git repository
log_info "Synchronizing test results to local Git repository..."

# Use rsync instead of cp for better error handling if available
if command -v rsync &> /dev/null; then
    if [ -d "$LOCAL_PROJECT_DIR/docker/test-results" ]; then
        rsync -av "$LOCAL_PROJECT_DIR/docker/test-results/" "$LOCAL_GIT_DIR/test-results/"
        log_success "Test results synchronized using rsync to: $LOCAL_GIT_DIR/test-results/"
    else
        log_warning "No test results found in $LOCAL_PROJECT_DIR/docker/test-results/"
    fi
else
    # Fallback to cp with better error handling
    if [ -d "$LOCAL_PROJECT_DIR/docker/test-results" ] && [ "$(ls -A "$LOCAL_PROJECT_DIR/docker/test-results/")" ]; then
        cp -r "$LOCAL_PROJECT_DIR/docker/test-results/"* "$LOCAL_GIT_DIR/test-results/" || log_error "Failed to copy test results"
        log_success "Test results synchronized using cp to: $LOCAL_GIT_DIR/test-results/"
    else
        log_warning "No test results found in $LOCAL_PROJECT_DIR/docker/test-results/"
    fi
fi

# Show available test results
echo ""
log_info "Available test results in Git repository:"
find "$LOCAL_GIT_DIR/test-results/" -type f -name "*.txt" -o -name "*.log" | sort

# Touch a marker file to indicate sync was attempted
touch "$LOCAL_GIT_DIR/test-results/.last_sync_$(date +%Y%m%d_%H%M%S)" 