#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Test Executor
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
TEST_PATTERN=""

parse_exec_args() {
    for arg in "$@"; do
        case $arg in
            --type=*)
                TEST_TYPE="${arg#*=}"
                ;;
            --pattern=*)
                TEST_PATTERN="${arg#*=}"
                ;;
            *)
                parse_args "$arg" # Pass to common arg parser
                ;;
        esac
    done
}

parse_exec_args "$@"

# ------------------------------------------------------
# Get timestamp for unique filenames
# ------------------------------------------------------
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="test_results_${TEST_TYPE}_${TIMESTAMP}.txt"

# ------------------------------------------------------
# Main Test Function
# ------------------------------------------------------
run_remote_tests() {
    log_info "Running ${TEST_TYPE} tests on ${SERVER_HOST}..."
    
    # Basic test command
    local test_cmd="cd ${PROJECT_ROOT_DIR} && docker exec discord-server-bot pytest -xvs"
    
    # Add test type path
    case "$TEST_TYPE" in
        "unit")
            test_cmd="${test_cmd} tests/unit/"
            ;;
        "integration")
            test_cmd="${test_cmd} tests/integration/"
            ;;
        "system")
            test_cmd="${test_cmd} tests/system/"
            ;;
        "all"|*)
            test_cmd="${test_cmd} tests/"
            ;;
    esac
    
    # Add pattern if specified
    if [ -n "$TEST_PATTERN" ]; then
        test_cmd="${test_cmd} -k \"${TEST_PATTERN}\""
    fi
    
    # Run the tests
    local test_result_file="${SERVER_RESULTS_DIR}/test_results_${TEST_TYPE}_${TIMESTAMP}.txt"
    run_remote_command "${test_cmd} | tee ${test_result_file}"
    
    return $?
}

# ------------------------------------------------------
# Download test results
# ------------------------------------------------------
download_results() {
    log_info "Downloading test results..."
    LATEST_RESULTS=$(run_remote_command "ls -t /tmp/test_results_${TEST_TYPE}_* | head -1")
    
    if [ -z "$LATEST_RESULTS" ]; then
        log_error "No test results found on server."
        return 1
    fi
    
    # Create results directory if it doesn't exist
    mkdir -p "$LOCAL_RESULTS_DIR"
    
    # Download the file
    download_file "$LATEST_RESULTS" "$LOCAL_RESULTS_DIR/$(basename "$LATEST_RESULTS")"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to download test results."
        return 1
    fi
    
    LOCAL_FILE="$LOCAL_RESULTS_DIR/$(basename "$LATEST_RESULTS")"
    log_success "Test results saved to: $LOCAL_FILE"
    
    # Display test results
    log_section "Test Results"
    cat "$LOCAL_FILE"
    
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
    
    # Run tests on remote server
    run_remote_tests
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Download test results
    download_results
    
    log_success "Testing completed successfully."
}

# Run the main function
main 