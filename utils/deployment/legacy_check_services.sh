#!/usr/bin/env bash

# Check if required services are running on the remote server

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Server settings
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"

echo "Checking services on ${SERVER_HOST}..."

# Check if Docker is running
docker_status=$(ssh ${SERVER_USER}@${SERVER_HOST} "systemctl is-active docker" 2>/dev/null)
if [ "$docker_status" = "active" ]; then
    echo -e "${GREEN}Docker is running.${NC}"
    docker_running=true
else
    echo -e "${RED}Docker is not running.${NC}"
    docker_running=false
fi

# Check if the Discord bot container is running
bot_running=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker ps -q -f name=homelab-discord-bot" 2>/dev/null)
if [ -n "$bot_running" ]; then
    echo -e "${GREEN}HomeLab Discord Bot is running.${NC}"
else
    echo -e "${RED}HomeLab Discord Bot is not running.${NC}"
    exit_code=1
fi

# Check if PostgreSQL is running
postgres_running=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker ps -q -f name=homelab-postgres" 2>/dev/null)
if [ -n "$postgres_running" ]; then
    echo -e "${GREEN}PostgreSQL is running.${NC}"
else
    echo -e "${RED}PostgreSQL is not running.${NC}"
    exit_code=1
fi

# Check if Redis is running
redis_running=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker ps -q -f name=homelab-redis" 2>/dev/null)
if [ -n "$redis_running" ]; then
    echo -e "${GREEN}Redis is running.${NC}"
else
    echo -e "${RED}Redis is not running.${NC}"
    exit_code=1
fi

echo -e "${YELLOW}Service check completed.${NC}"
exit ${exit_code:-0} 