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

parse_exec_args() {
    for arg in "$@"; do
        case $arg in
            --type=*)
                TEST_TYPE="${arg#*=}"
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
    log_info "Running tests on remote server..."
    
    # First determine the remote shell
    REMOTE_SHELL=$(run_remote_command "echo \$SHELL")
    log_info "Remote shell: $REMOTE_SHELL"
    
    # Create a temporary script with appropriate shebang line
    TMP_SCRIPT_FILE="/tmp/test_script_${TIMESTAMP}.sh"
    cat > "$TMP_SCRIPT_FILE" << EOL
#!/usr/bin/env bash

# Set up the environment
export PYTHONPATH=/
cd $PROJECT_ROOT_DIR

# Get timestamp for unique filenames
TIMESTAMP=\$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="test_results_${TEST_TYPE}_\${TIMESTAMP}.txt"

# Initialize result file
echo ">>> Running ${TEST_TYPE} tests..." > "/tmp/\$RESULTS_FILE"
echo ">>> Started at: \$(date)" >> "/tmp/\$RESULTS_FILE"
echo "Running tests using Docker container Python" >> "/tmp/\$RESULTS_FILE"

# Directory structure information
echo -e "\n=== CONTAINER DIRECTORY STRUCTURE ===" >> "/tmp/\$RESULTS_FILE"
docker exec $BOT_CONTAINER sh -c "ls -la /app/bot" >> "/tmp/\$RESULTS_FILE"
echo -e "\nPython path:" >> "/tmp/\$RESULTS_FILE"
docker exec $BOT_CONTAINER python -c "import sys; print('\n'.join(sys.path))" >> "/tmp/\$RESULTS_FILE"

# Run the tests based on type
echo -e "\n=== RUNNING TESTS IN CONTAINER ===" >> "/tmp/\$RESULTS_FILE"

case "$TEST_TYPE" in
  "unit")
    echo "Running unit tests only" >> "/tmp/\$RESULTS_FILE"
    docker exec -w /app/bot $BOT_CONTAINER sh -c "PYTHONPATH=/ python -m pytest tests/unit -v" >> "/tmp/\$RESULTS_FILE" 2>&1
    ;;
  "integration")
    echo "Running integration tests only" >> "/tmp/\$RESULTS_FILE"
    docker exec -w /app/bot $BOT_CONTAINER sh -c "PYTHONPATH=/ python -m pytest tests/integration -v" >> "/tmp/\$RESULTS_FILE" 2>&1
    ;;
  "system")
    echo "Running system tests only" >> "/tmp/\$RESULTS_FILE"
    docker exec -w /app/bot $BOT_CONTAINER sh -c "PYTHONPATH=/ python -m pytest tests/system -v" >> "/tmp/\$RESULTS_FILE" 2>&1
    ;;
  "all"|*)
    echo "Running all tests" >> "/tmp/\$RESULTS_FILE"
    docker exec -w /app/bot $BOT_CONTAINER sh -c "PYTHONPATH=/ python -m pytest tests -v" >> "/tmp/\$RESULTS_FILE" 2>&1
    ;;
esac

echo ">>> Tests completed at: \$(date)" >> "/tmp/\$RESULTS_FILE"
echo "Tests completed. Results saved to /tmp/\$RESULTS_FILE"
exit 0
EOL

    # Upload the script
    upload_file "$TMP_SCRIPT_FILE" "/tmp/run_tests.sh"
    
    # Make it executable
    run_remote_command "chmod +x /tmp/run_tests.sh"
    
    # Run the script
    log_info "Executing test script..."
    run_remote_command "/tmp/run_tests.sh"
    
    if [ $? -ne 0 ]; then
        log_error "Error executing tests on remote server."
        return 1
    fi
    
    return 0
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