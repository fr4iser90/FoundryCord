#!/usr/bin/env bash

# Remote Docker Testing Script for HomeLab Discord Bot
# This script runs tests on a remote server and retrieves the results

# Variables (matching your deployment setup)
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
PROJECT_ROOT_DIR="/home/docker/docker/companion-management/homelab-discord-bot"
DOCKER_DIR="${PROJECT_ROOT_DIR}/compose"
LOCAL_RESULTS_DIR="./test-results"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Create local directory for results if it doesn't exist
mkdir -p "$LOCAL_RESULTS_DIR"

# Get timestamp for unique filenames
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="web_test_results_${TIMESTAMP}.txt"
COVERAGE_FILE="web_coverage_${TIMESTAMP}.html"

echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}     HomeLab Discord Bot - Remote Testing Script         ${NC}"
echo -e "${YELLOW}=========================================================${NC}"
echo -e "${YELLOW}Remote Host:${NC} $SERVER_HOST"
echo -e "${YELLOW}Remote Path:${NC} $PROJECT_ROOT_DIR"
echo -e "${YELLOW}Starting tests at:${NC} $(date)"
echo -e "${YELLOW}=========================================================${NC}\n"

# Function to check if SSH connection is successful
check_ssh_connection() {
    echo -e "${YELLOW}Checking SSH connection...${NC}"
    if ssh "$SERVER_USER@$SERVER_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
        echo -e "${GREEN}SSH connection successful!${NC}\n"
        return 0
    else
        echo -e "${RED}Error: Could not connect to remote server via SSH.${NC}"
        echo "Please check your SSH credentials and server status."
        return 1
    fi
}

# Function to run tests on the remote server
run_remote_tests() {
    echo -e "${YELLOW}Running tests on remote server...${NC}"
    
    # First determine the remote shell
    REMOTE_SHELL=$(ssh "$SERVER_USER@$SERVER_HOST" "echo \$SHELL")
    echo "Remote shell: $REMOTE_SHELL"
    
    # Create a temporary script with appropriate shebang line
    cat > /tmp/local_test_script.sh << 'EOF'
#!/usr/bin/env bash

# Set up the environment
export PYTHONPATH=/home/docker/docker/companion-management/homelab-discord-bot
cd /home/docker/docker/companion-management/homelab-discord-bot

# Get timestamp for unique filenames
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="web_test_results_${TIMESTAMP}.txt"

# Initialize result file
echo ">>> Running web interface tests..." > "/tmp/$RESULTS_FILE"
echo ">>> Started at: $(date)" >> "/tmp/$RESULTS_FILE"
echo "Running tests using Docker container Python" >> "/tmp/$RESULTS_FILE"

# First, explore the directory structure on the host
echo -e "\n=== HOST DIRECTORY STRUCTURE ===" >> "/tmp/$RESULTS_FILE"
echo "Current directory on host:" >> "/tmp/$RESULTS_FILE"
pwd >> "/tmp/$RESULTS_FILE"
echo -e "\nListing all directories in current path:" >> "/tmp/$RESULTS_FILE"
ls -la >> "/tmp/$RESULTS_FILE"
echo -e "\nListing tests directory (if exists):" >> "/tmp/$RESULTS_FILE"
ls -la tests/ 2>&1 >> "/tmp/$RESULTS_FILE"

# Now explore the container's filesystem
echo -e "\n=== CONTAINER DIRECTORY STRUCTURE ===" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot sh -c "echo 'Current working directory in container:' && pwd" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot sh -c "echo -e '\nRoot directory listing:' && ls -la /" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot sh -c "echo -e '\n/app directory listing:' && ls -la /app" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot sh -c "echo -e '\n/app/bot directory listing:' && ls -la /app/bot" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot sh -c "echo -e '\nPython module search path:' && python -c 'import sys; print(\"\n\".join(sys.path))'" >> "/tmp/$RESULTS_FILE"

# Now try to copy test files to the right place in the container
echo -e "\n=== COPYING TEST FILES TO CONTAINER ===" >> "/tmp/$RESULTS_FILE"
echo "Creating tests directory in container..." >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot mkdir -p /app/bot/tests >> "/tmp/$RESULTS_FILE" 2>&1

echo "Copying test files from host to container..." >> "/tmp/$RESULTS_FILE"
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    for test_file in tests/test_*.py; do
        if [ -f "$test_file" ]; then
            echo "Copying $test_file to container..." >> "/tmp/$RESULTS_FILE"
            docker cp "$test_file" homelab-discord-bot:/app/bot/tests/ >> "/tmp/$RESULTS_FILE" 2>&1
        fi
    done
else
    echo "No test files found in host tests directory" >> "/tmp/$RESULTS_FILE"
fi

echo "Listing tests directory in container after copy:" >> "/tmp/$RESULTS_FILE"
docker exec homelab-discord-bot ls -la /app/bot/tests >> "/tmp/$RESULTS_FILE" 2>&1

# Modify Python path in container for correct imports
echo -e "\n=== SETTING UP PYTHON PATH ===" >> "/tmp/$RESULTS_FILE"
echo "Setting PYTHONPATH to include root directory for proper imports" >> "/tmp/$RESULTS_FILE"

# Now try to run the tests with the corrected PYTHONPATH
echo -e "\n=== RUNNING TESTS IN CONTAINER ===" >> "/tmp/$RESULTS_FILE"
docker exec -w /app/bot homelab-discord-bot sh -c "PYTHONPATH=/ python -m pytest tests -v" >> "/tmp/$RESULTS_FILE" 2>&1

echo ">>> Tests completed at: $(date)" >> "/tmp/$RESULTS_FILE"
echo "Tests completed. Results saved to /tmp/$RESULTS_FILE"
exit 0
EOF

    # Upload the script
    scp /tmp/local_test_script.sh "$SERVER_USER@$SERVER_HOST:/tmp/run_tests.sh"
    
    # Make it executable
    ssh "$SERVER_USER@$SERVER_HOST" "chmod +x /tmp/run_tests.sh"
    
    # Run the script
    echo "Executing test script..."
    ssh "$SERVER_USER@$SERVER_HOST" "/tmp/run_tests.sh"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error executing tests on remote server.${NC}"
        return 1
    fi
    
    return 0
}

# Function to download test results
download_results() {
    echo "Downloading test results..."
    LATEST_RESULTS=$(ssh "$SERVER_USER@$SERVER_HOST" "ls -t /tmp/web_test_results_* | head -1")
    
    if [ -z "$LATEST_RESULTS" ]; then
        echo -e "${RED}Error: No test results found on server.${NC}"
        return 1
    fi
    
    scp "$SERVER_USER@$SERVER_HOST:$LATEST_RESULTS" "$LOCAL_RESULTS_DIR/" > /dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to download test results.${NC}"
        return 1
    fi
    
    LOCAL_FILE=$(basename "$LATEST_RESULTS")
    echo -e "${GREEN}Test results saved to:${NC} $LOCAL_RESULTS_DIR/$LOCAL_FILE"
    
    # Display test results
    echo -e "\n${YELLOW}=== Test Results ===${NC}"
    cat "$LOCAL_RESULTS_DIR/$LOCAL_FILE"
    
    return 0
}

# Main function
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
    
    echo -e "\n${GREEN}Testing completed successfully.${NC}"
}

# Run the main function
main 