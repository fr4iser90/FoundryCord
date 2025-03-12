#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Common Utility Functions
# =======================================================

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

# Check SSH connection to server
check_ssh_connection() {
    log_info "Testing SSH connection to ${SERVER_HOST}..."
    
    if ssh -q -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_HOST}" exit; then
        log_success "SSH connection successful!"
        return 0
    else
        log_error "SSH connection failed!"
        return 1
    fi
}

# Run command on remote server
run_remote_command() {
    local cmd="$1"
    local silent="${2:-false}"
    
    if [ "$silent" = "true" ]; then
        ssh "${SERVER_USER}@${SERVER_HOST}" "$cmd" > /dev/null 2>&1
    else
        ssh "${SERVER_USER}@${SERVER_HOST}" "$cmd"
    fi
    
    return $?
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
            --env=*)
                export ENVIRONMENT="${arg#*=}"
                # Re-source config to load environment-specific settings
                source "$(dirname "$0")/../config/config.sh"
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