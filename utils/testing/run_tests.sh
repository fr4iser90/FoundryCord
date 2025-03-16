#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Main Test Runner
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Command-line Arguments Parsing
# ------------------------------------------------------
TEST_TYPE="all"
DEPLOY_FIRST=true
SKIP_CHECKS=false

parse_test_args() {
    for arg in "$@"; do
        case $arg in
            --type=*)
                TEST_TYPE="${arg#*=}"
                ;;
            --deploy)
                DEPLOY_FIRST=true
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                ;;
            *)
                parse_args "$arg" # Pass to common arg parser
                ;;
        esac
    done
}

parse_test_args "$@"

# ------------------------------------------------------
# Main Testing Process
# ------------------------------------------------------
main() {
    log_section "HomeLab Discord Bot - Complete Testing Suite"
    
    # Optional deployment step
    if [ "$DEPLOY_FIRST" = "true" ]; then
        log_section "STEP 1: Deploying code changes"
        ./utils/deployment/deploy.sh
        
        if [ $? -ne 0 ]; then
            log_error "Deployment failed. Aborting tests."
            exit 1
        fi
    fi
    
    # Service health checks
    if [ "$SKIP_CHECKS" != "true" ]; then
        log_section "STEP 2: Checking services"
        ./utils/deployment/check_services.sh
        
        # Ask to restart services if needed
        if [ $? -ne 0 ]; then
            if [ "$AUTO_RESTART" = "true" ]; then
                log_info "Some services are not running. Restarting Docker stack..."
                ./utils/deployment/update_docker.sh
                
                # Check again
                log_info "Checking services after restart..."
                ./utils/deployment/check_services.sh
                
                if [ $? -ne 0 ]; then
                    log_error "Services still not running after restart. Aborting tests."
                    exit 1
                fi
            else
                read -p "Some services are not running. Would you like to restart the Docker stack? (y/n): " restart_services
                if [ "$restart_services" = "y" ]; then
                    log_info "Restarting Docker services..."
                    ./utils/deployment/update_docker.sh
                    
                    log_info "Checking services after restart..."
                    ./utils/deployment/check_services.sh
                else
                    read -p "Continue with testing anyway? (y/n): " continue_anyway
                    if [ "$continue_anyway" != "y" ]; then
                        log_error "Testing aborted."
                        exit 1
                    fi
                fi
            fi
        fi
    fi
    
    # Upload test files
    log_section "STEP 3: Uploading test files"
    ./utils/testing/upload_tests.sh
    
    if [ $? -ne 0 ]; then
        log_error "Failed to upload test files. Aborting tests."
        exit 1
    fi
    
    # Run tests based on type
    log_section "STEP 4: Running tests"
    
    case "$TEST_TYPE" in
        "unit")
            log_info "Running unit tests only"
            ./utils/testing/test.sh --type=unit
            ;;
        "integration")
            log_info "Running integration tests only"
            ./utils/testing/test.sh --type=integration
            ;;
        "system")
            log_info "Running system tests only"
            ./utils/testing/test.sh --type=system
            ;;
        "all"|*)
            log_info "Running all tests"
            ./utils/testing/test.sh
            ;;
    esac
    
    log_success "Complete testing process finished."
}

# Run the main function
main 


