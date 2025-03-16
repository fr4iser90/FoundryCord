#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Common Utility Functions
# =======================================================

# Color codes for terminal output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[0;33m'
export BLUE='\033[0;34m'
export NC='\033[0m' # No Color

# Check if config is loaded, if not, load it
if [ -z "$CONFIG_LOADED" ]; then
    source "$(dirname "$0")/../config/config.sh"
fi

# ------------------------------------------------------
# Common Utility Functions
# ------------------------------------------------------

# Print a message with timestamp
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] [WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] [ERROR]${NC} $message"
            ;;
        *)
            echo -e "[${timestamp}] $message"
            ;;
    esac
}

# Log info message
log_info() {
    log "INFO" "$1"
}

# Log success message
log_success() {
    log "SUCCESS" "$1"
}

# Log warning message
log_warning() {
    log "WARNING" "$1"
}

# Log error message
log_error() {
    log "ERROR" "$1"
}

# Execute command and handle errors
execute_command() {
    local command="$1"
    local error_message="${2:-Command failed}"
    
    if ! eval "$command"; then
        log_error "$error_message"
        return 1
    fi
    
    return 0
}

# Validate configuration and ensure required variables are set
validate_config() {
    local missing_vars=()
    local config_valid=true
    
    # Only validate connection settings if not running locally
    if [ "$RUN_LOCALLY" = false ]; then
        # Check server connection settings
        [ -z "$SERVER_USER" ] && missing_vars+=("SERVER_USER") && config_valid=false
        [ -z "$SERVER_HOST" ] && missing_vars+=("SERVER_HOST") && config_valid=false
        [ -z "$SERVER_PORT" ] && missing_vars+=("SERVER_PORT") && config_valid=false
    fi
    
    # If configuration is incomplete, show a setup dialog
    if [ "$config_valid" = false ]; then
        clear
        echo -e "${YELLOW}=========================================================${NC}"
        echo -e "${YELLOW}     Initial Configuration Required                      ${NC}"
        echo -e "${YELLOW}=========================================================${NC}"
        echo -e "${RED}Some required configuration settings are missing:${NC}"
        
        for var in "${missing_vars[@]}"; do
            echo -e " - ${var}"
        done
        
        echo ""
        echo -e "Let's set up your configuration now."
        echo ""
        
        configure_settings
    fi
}

# Check SSH connection to remote server
check_ssh_connection() {
    local silent_mode="$1"
    
    if [ "$RUN_LOCALLY" = true ]; then
        [ "$silent_mode" != "silent" ] && echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Running in local mode, skipping SSH check.${NC}"
        return 0
    fi
    
    [ "$silent_mode" != "silent" ] && echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Testing SSH connection to ${SERVER_HOST}...${NC}"
    
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "echo 2>&1" > /dev/null; then
        [ "$silent_mode" != "silent" ] && echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] Cannot connect to ${SERVER_HOST}.${NC}"
        [ "$silent_mode" != "silent" ] && echo -e "${YELLOW}Please check your SSH configuration and ensure you have key-based authentication set up.${NC}"
        return 1
    fi
    
    [ "$silent_mode" != "silent" ] && echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] SSH connection successful!${NC}"
    
    # Check if project directory exists
    if [ -n "$PROJECT_ROOT_DIR" ]; then
        if ! ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "test -d ${PROJECT_ROOT_DIR}" > /dev/null 2>&1; then
            [ "$silent_mode" != "silent" ] && echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] Project directory ${PROJECT_ROOT_DIR} does not exist on remote server.${NC}"
            
            # Ask to create directory
            if [ "$silent_mode" != "silent" ] && get_yes_no "Would you like to create the project directory?"; then
                ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${PROJECT_ROOT_DIR}"
                echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] Created directory ${PROJECT_ROOT_DIR}${NC}"
            fi
        fi
    fi
    
    return 0
}

# Run command on remote server
run_remote_command() {
    local command="$1"
    local silent_mode="$2"
    
    if [ "$RUN_LOCALLY" = true ]; then
        [ "$silent_mode" != "silent" ] && echo -e "${BLUE}[LOCAL MODE] Would run: ${command}${NC}"
        return 0
    fi
    
    [ "$silent_mode" != "silent" ] && echo -e "${BLUE}[REMOTE] ${command}${NC}"
    
    # Skip directory checks if command doesn't use DOCKER_DIR
    if ! echo "$command" | grep -q "cd \${DOCKER_DIR}"; then
        ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "$command"
        return $?
    fi
    
    # Check if DOCKER_DIR exists
    if ! ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "test -d ${DOCKER_DIR}" > /dev/null 2>&1; then
        [ "$silent_mode" != "silent" ] && echo -e "${YELLOW}[WARNING] Docker directory not found: ${DOCKER_DIR}${NC}"
        
        if [ "$silent_mode" != "silent" ] && get_yes_no "Would you like to create the Docker directory?"; then
            ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${DOCKER_DIR}"
            echo -e "${GREEN}[SUCCESS] Created Docker directory.${NC}"
        else
            [ "$silent_mode" != "silent" ] && echo -e "${RED}[ERROR] Cannot execute command without a valid Docker directory.${NC}"
            return 1
        fi
    fi
    
    # Now run the actual command
    ssh -p "${SERVER_PORT}" "${SERVER_USER}@${SERVER_HOST}" "$command"
    return $?
}

# Get yes/no input
get_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local input
    
    if [ "$default" = "y" ]; then
        read -p "$prompt [Y/n]: " input
        input=${input:-y}
    else
        read -p "$prompt [y/N]: " input
        input=${input:-n}
    fi
    
    case "$input" in
        [Yy]*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Check if docker-compose.yml exists (for both bot and web)
check_docker_compose_files() {
    log_info "Checking for docker-compose files..."
    
    if run_remote_command "test -f ${BOT_COMPOSE_FILE}" "true"; then
        log_success "Bot docker-compose.yml exists."
    else
        log_error "Bot docker-compose.yml NOT found at ${BOT_COMPOSE_FILE}"
        return 1
    fi
    
    if run_remote_command "test -f ${WEB_COMPOSE_FILE}" "true"; then
        log_success "Web docker-compose.yml exists."
    else
        log_warning "Web docker-compose.yml NOT found at ${WEB_COMPOSE_FILE}"
        # Not returning error as web might be optional
    fi
    
    return 0
}

# ------------------------------------------------------
# Docker Functions
# ------------------------------------------------------
is_container_running() {
    local container_name="$1"
    run_remote_command "docker ps -q -f name=$container_name" "true" | grep -q .
    return $?
}

get_container_id() {
    local container_name="$1"
    run_remote_command "docker ps -qf \"name=$container_name\""
}

restart_container() {
    local container_name="$1"
    log_info "Restarting container: $container_name"
    run_remote_command "docker restart $container_name"
}

run_in_container() {
    local container_name="$1"
    local cmd="$2"
    local workdir="${3:-/app/bot}"
    
    run_remote_command "docker exec -w $workdir $container_name $cmd"
    return $?
}

# ------------------------------------------------------
# File Functions
# ------------------------------------------------------
upload_file() {
    local local_path="$1"
    local remote_path="$2"
    
    # Create remote directory if it doesn't exist
    local remote_dir=$(dirname "$remote_path")
    run_remote_command "mkdir -p $remote_dir" "true"
    
    # Upload the file
    scp -i "$SERVER_KEY" -P "$SERVER_PORT" "$local_path" "$SERVER_USER@$SERVER_HOST:$remote_path"
    return $?
}

download_file() {
    local remote_path="$1"
    local local_path="$2"
    
    # Create local directory if it doesn't exist
    local local_dir=$(dirname "$local_path")
    mkdir -p "$local_dir"
    
    # Download the file
    scp -i "$SERVER_KEY" -P "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST:$remote_path" "$local_path"
    return $?
}

# ------------------------------------------------------
# Argument Parsing Helper
# ------------------------------------------------------
parse_args() {
    for arg in "$@"; do
        case $arg in
            --host=*)
                export SERVER_HOST="${arg#*=}"
                ;;
            --user=*)
                export SERVER_USER="${arg#*=}"
                ;;
            --port=*)
                export SERVER_PORT="${arg#*=}"
                ;;
            --key=*)
                export SERVER_KEY="${arg#*=}"
                ;;
            --no-restart)
                export AUTO_RESTART="false"
                ;;
            --rebuild)
                export REBUILD_ON_DEPLOY="true"
                ;;
            --help)
                show_help
                exit 0
                ;;
        esac
    done
}

show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --host=HOST         Specify the remote host (default: $SERVER_HOST)"
    echo "  --user=USER         Specify the remote user (default: $SERVER_USER)"
    echo "  --port=PORT         Specify the SSH port (default: $SERVER_PORT)"
    echo "  --key=KEY           Specify the SSH key file (default: $SERVER_KEY)"
    echo "  --env=ENV           Specify environment (dev, staging, prod)"
    echo "  --no-restart        Don't automatically restart services"
    echo "  --rebuild           Force rebuild of Docker containers"
    echo "  --help              Show this help message"
}

# Log a section header
log_section() {
    local message="$1"
    echo ""
    echo -e "${YELLOW}=== ${message} ===${NC}"
    echo ""
} 