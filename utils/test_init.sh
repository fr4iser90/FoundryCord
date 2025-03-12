#!/run/current-system/sw/bin/bash

# Initialize test environment

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Ensure the utils directory exists
mkdir -p utils

# Check if test.sh exists
if [ ! -f utils/test.sh ]; then
    echo -e "${RED}Error: utils/test.sh does not exist.${NC}"
    exit 1
fi

# Make sure test.sh is executable
chmod +x utils/test.sh

# Create local config file if it doesn't exist
if [ ! -f utils/test_config_local.sh ]; then
    if [ -f utils/test_config.sh ]; then
        cp utils/test_config.sh utils/test_config_local.sh
        echo -e "${YELLOW}Created utils/test_config_local.sh.${NC}"
        echo -e "${YELLOW}Please edit this file with your remote server settings.${NC}"
    else
        echo -e "${RED}Error: utils/test_config.sh does not exist.${NC}"
        exit 1
    fi
fi

# Create test-results directory
mkdir -p test-results
echo -e "${GREEN}Created test-results directory.${NC}"

echo -e "${GREEN}Test environment initialized successfully.${NC}"
echo -e "${YELLOW}To run tests:${NC} bash utils/test.sh" 