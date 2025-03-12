#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Display Functions
# =======================================================

# Display header with dynamic content
show_header() {
    clear
    echo -e "${YELLOW}=========================================================${NC}"
    echo -e "${YELLOW}     HomeLab Discord Bot - Central Management Tool       ${NC}"
    echo -e "${YELLOW}=========================================================${NC}"
    echo -e "${YELLOW}Current Settings:${NC}"
    echo -e "  Server: ${GREEN}${SERVER_USER}@${SERVER_HOST}${NC}"
    echo -e "  Environment: ${GREEN}${ENVIRONMENT:-dev}${NC}"
    
    # Show environment variables status
    local env_status=""
    if [ -n "$DISCORD_BOT_TOKEN" ]; then
        env_status="${GREEN}Loaded${NC}"
    else
        env_status="${YELLOW}Not loaded${NC}"
    fi
    echo -e "  Environment Variables: $env_status"
    
    # Show running containers if possible
    if [ "$RUN_LOCALLY" = false ] && check_ssh_connection "silent"; then
        RUNNING_CONTAINERS=$(run_remote_command "cd ${DOCKER_DIR} && docker compose ps --services --filter \"status=running\"" "silent")
        if [ -n "$RUNNING_CONTAINERS" ]; then
            echo -e "  Running containers: ${GREEN}${RUNNING_CONTAINERS//$'\n'/, }${NC}"
        else
            echo -e "  Running containers: ${YELLOW}None${NC}"
        fi
    fi
    
    echo -e "${YELLOW}=========================================================${NC}"
    echo ""
}

# Print section header
print_section_header() {
    local title="$1"
    echo -e "${YELLOW}${title}${NC}"
    echo -e "${YELLOW}$(printf '%*s' "${#title}" | tr ' ' '-')${NC}"
}

# Print numbered menu item
print_menu_item() {
    local number="$1"
    local description="$2"
    echo -e "${number}. ${GREEN}${description}${NC}"
}

# Print back menu item
print_back_option() {
    echo -e "0. ${RED}Back to Previous Menu${NC}"
}

# Print exit option
print_exit_option() {
    echo -e "0. ${RED}Exit${NC}"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Print success message
print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Print info message
print_info() {
    echo -e "${BLUE}INFO: $1${NC}"
} 