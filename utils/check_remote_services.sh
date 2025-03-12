#!/bin/bash

# Check if required services are running on the remote server

# Configuration (can be overridden by environment variables)
REMOTE_HOST=${REMOTE_HOST:-"your-server.example.com"}
REMOTE_USER=${REMOTE_USER:-"ubuntu"}
REMOTE_KEY=${REMOTE_KEY:-"$HOME/.ssh/id_rsa"}
REMOTE_PORT=${REMOTE_PORT:-22}

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Import local configuration if it exists
if [ -f utils/test_config_local.sh ]; then
    source utils/test_config_local.sh
fi

echo -e "${YELLOW}Checking services on ${REMOTE_HOST}...${NC}"

# Check Docker status
docker_status=$(ssh -i "$REMOTE_KEY" -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "systemctl is-active docker 2>/dev/null || echo 'not installed'")
if [ "$docker_status" = "active" ]; then
    echo -e "${GREEN}Docker is running.${NC}"
else
    echo -e "${RED}Docker is not running or not installed.${NC}"
fi

# Check if PostgreSQL is available
pg_status=$(ssh -i "$REMOTE_KEY" -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "docker ps | grep postgres || echo 'not running'")
if [[ "$pg_status" == *"postgres"* ]]; then
    echo -e "${GREEN}PostgreSQL is running in Docker.${NC}"
else
    echo -e "${RED}PostgreSQL is not running in Docker.${NC}"
fi

# Check if Redis is available
redis_status=$(ssh -i "$REMOTE_KEY" -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "docker ps | grep redis || echo 'not running'")
if [[ "$redis_status" == *"redis"* ]]; then
    echo -e "${GREEN}Redis is running in Docker.${NC}"
else
    echo -e "${RED}Redis is not running in Docker.${NC}"
fi

echo -e "${YELLOW}Service check completed.${NC}" 