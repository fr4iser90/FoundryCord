#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Service Health Checker
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
INFO="${YELLOW}[INFO]${NC}"
SUCCESS="${GREEN}[SUCCESS]${NC}"
ERROR="${RED}[ERROR]${NC}"
NC='\033[0m' # No Color

# ------------------------------------------------------
# Command-line Arguments Parsing
# ------------------------------------------------------
VERBOSE=false

parse_checker_args() {
    for arg in "$@"; do
        case $arg in
            --verbose)
                VERBOSE=true
                ;;
            *)
                parse_args "$arg" # Pass to common arg parser
                ;;
        esac
    done
}

parse_checker_args "$@"

# ------------------------------------------------------
# Service Checking Functions
# ------------------------------------------------------
check_docker() {
    local docker_status=$(run_remote_command "systemctl is-active docker" "true")
    
    if [ "$docker_status" = "active" ]; then
        if [ "$VERBOSE" = "true" ]; then
            log_success "Docker is running."
        else
            echo -e "${GREEN}Docker is running.${NC}"
        fi
        return 0
    else
        if [ "$VERBOSE" = "true" ]; then
            log_error "Docker is not running."
        else
            echo -e "${RED}Docker is not running.${NC}"
        fi
        return 1
    fi
}

check_bot() {
    if is_container_running "$BOT_CONTAINER"; then
        if [ "$VERBOSE" = "true" ]; then
            log_success "HomeLab Discord Bot is running."
        else
            echo -e "${GREEN}HomeLab Discord Bot is running.${NC}"
        fi
        return 0
    else
        if [ "$VERBOSE" = "true" ]; then
            log_error "HomeLab Discord Bot is not running."
        else
            echo -e "${RED}HomeLab Discord Bot is not running.${NC}"
        fi
        return 1
    fi
}

check_postgres() {
    if is_container_running "$POSTGRES_CONTAINER"; then
        if [ "$VERBOSE" = "true" ]; then
            log_success "PostgreSQL is running."
        else
            echo -e "${GREEN}PostgreSQL is running.${NC}"
        fi
        return 0
    else
        if [ "$VERBOSE" = "true" ]; then
            log_error "PostgreSQL is not running."
        else
            echo -e "${RED}PostgreSQL is not running.${NC}"
        fi
        return 1
    fi
}

check_redis() {
    if is_container_running "$REDIS_CONTAINER"; then
        if [ "$VERBOSE" = "true" ]; then
            log_success "Redis is running."
        else
            echo -e "${GREEN}Redis is running.${NC}"
        fi
        return 0
    else
        if [ "$VERBOSE" = "true" ]; then
            log_error "Redis is not running."
        else
            echo -e "${RED}Redis is not running.${NC}"
        fi
        return 1
    fi
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    echo -e "${INFO} Checking services on ${SERVER_HOST}..."
    echo -e "${INFO} Checking SSH connection to ${SERVER_HOST}..."

    # Test SSH connection first
    if ssh -q "${SERVER_USER}@${SERVER_HOST}" exit; then
        echo -e "${SUCCESS} SSH connection successful!"
    else
        echo -e "${ERROR} SSH connection failed! Please check your SSH setup."
        exit 1
    fi

    # Check if Docker is running by directly checking for containers
    # This is more reliable than checking the systemd service
    docker_running=$(ssh "${SERVER_USER}@${SERVER_HOST}" "docker ps >/dev/null 2>&1 && echo 'running' || echo 'not running'")

    if [ "$docker_running" = "running" ]; then
        echo -e "${SUCCESS} Docker is running."
        docker_running=true
    else
        echo -e "${ERROR} Docker is not running."
        docker_running=false
        exit_code=1
    fi

    # Check if the Discord bot container is running
    bot_running=$(ssh "${SERVER_USER}@${SERVER_HOST}" "docker ps -q -f name=homelab-discord-bot" 2>/dev/null)
    if [ -n "$bot_running" ]; then
        echo -e "${SUCCESS} HomeLab Discord Bot is running."
    else
        echo -e "${ERROR} HomeLab Discord Bot is not running."
        exit_code=1
    fi

    # Check if PostgreSQL is running
    postgres_running=$(ssh "${SERVER_USER}@${SERVER_HOST}" "docker ps -q -f name=homelab-postgres" 2>/dev/null)
    if [ -n "$postgres_running" ]; then
        echo -e "${SUCCESS} PostgreSQL is running."
    else
        echo -e "${ERROR} PostgreSQL is not running."
        exit_code=1
    fi

    # Check if Redis is running
    redis_running=$(ssh "${SERVER_USER}@${SERVER_HOST}" "docker ps -q -f name=homelab-redis" 2>/dev/null)
    if [ -n "$redis_running" ]; then
        echo -e "${SUCCESS} Redis is running."
    else
        echo -e "${ERROR} Redis is not running."
        exit_code=1
    fi

    if [ "${exit_code:-0}" -eq 0 ]; then
        echo -e "${SUCCESS} All services are running!"
    else
        echo -e "${ERROR} Some services are not running. Service check failed."
    fi

    exit ${exit_code:-0}
}

# Run the main function
main
exit $? 