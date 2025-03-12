#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Common Utility Functions
# =======================================================

# Source the main config if it hasn't been loaded
if [ -z "$CONFIG_LOADED" ]; then
    source "$(dirname "$0")/../config/config.sh"
fi

# ------------------------------------------------------
# Logging Functions
# ------------------------------------------------------
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${YELLOW}=========================================================${NC}"
    echo -e "${YELLOW}     $1${NC}"
    echo -e "${YELLOW}=========================================================${NC}\n"
}

# ------------------------------------------------------
# SSH Connection Functions
# ------------------------------------------------------
check_ssh_connection() {
    log_info "Checking SSH connection to ${SERVER_HOST}..."
    
    if ssh -i "$SERVER_KEY" -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
        log_success "SSH connection successful!"
        return 0
    else
        log_error "Could not connect to remote server via SSH."
        log_info "Please check your SSH credentials and server status."
        return 1
    fi
}

run_remote_command() {
    local cmd="$1"
    local silent="${2:-false}"
    
    if [ "$silent" = "true" ]; then
        ssh -i "$SERVER_KEY" -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST" "$cmd" > /dev/null 2>&1
    else
        ssh -i "$SERVER_KEY" -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST" "$cmd"
    fi
    
    return $?
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