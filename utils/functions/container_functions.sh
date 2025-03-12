#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Container Functions
# =======================================================

# Global variable for container list
declare -a CONTAINER_ACTIONS

# Load available containers
load_available_containers() {
    if [ "$RUN_LOCALLY" = true ]; then
        CONTAINER_ACTIONS=("bot" "postgres" "redis" "web" "web_db")
    else
        local containers=$(run_remote_command "cd ${DOCKER_DIR} && docker compose config --services" "silent")
        if [ -z "$containers" ]; then
            CONTAINER_ACTIONS=("bot" "postgres" "redis" "web" "web_db")
        else
            # Convert string to array
            IFS=$'\n' read -r -d '' -a CONTAINER_ACTIONS <<< "$containers"
        fi
    fi
}

# Show container status
show_container_status() {
    show_header
    print_section_header "Container Status"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot check container status in local mode"
    else
        run_remote_command "cd ${DOCKER_DIR} && docker compose ps"
    fi
    
    press_enter_to_continue
    show_container_menu
}

# Manage all containers
manage_all_containers() {
    local action="$1"
    show_header
    print_section_header "Managing all containers"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot manage containers in local mode"
    else
        case "$action" in
            "start")
                print_info "Starting all containers..."
                run_remote_command "cd ${DOCKER_DIR} && docker compose up -d"
                ;;
            "stop")
                print_info "Stopping all containers..."
                run_remote_command "cd ${DOCKER_DIR} && docker compose stop"
                ;;
            "restart")
                print_info "Restarting all containers..."
                run_remote_command "cd ${DOCKER_DIR} && docker compose restart"
                ;;
        esac
        print_success "Action completed"
    fi
    
    press_enter_to_continue
    show_container_menu
}

# Container action for individual container
container_action() {
    local container="$1"
    local action="$2"
    
    print_info "Performing '$action' on $container..."
    
    case "$action" in
        "start")
            run_remote_command "cd ${DOCKER_DIR} && docker compose up -d ${container}"
            ;;
        "stop")
            run_remote_command "cd ${DOCKER_DIR} && docker compose stop ${container}"
            ;;
        "restart")
            run_remote_command "cd ${DOCKER_DIR} && docker compose restart ${container}"
            ;;
    esac
    
    print_success "Action completed"
}

# View container logs
view_container_logs() {
    local container="$1"
    print_info "Viewing logs for ${container}..."
    run_remote_command "cd ${DOCKER_DIR} && docker compose logs --tail=100 -f ${container}"
}

# Rebuild single container
rebuild_single_container() {
    local container="$1"
    print_info "Rebuilding ${container}..."
    
    local no_cache=false
    if get_yes_no "Do you want to rebuild with no cache?"; then
        no_cache=true
    fi
    
    if [ "$no_cache" = true ]; then
        run_remote_command "cd ${DOCKER_DIR} && docker compose stop ${container} && docker compose build --no-cache ${container} && docker compose up -d ${container}"
    else
        run_remote_command "cd ${DOCKER_DIR} && docker compose stop ${container} && docker compose build ${container} && docker compose up -d ${container}"
    fi
    
    print_success "${container} rebuilt successfully"
}

# Execute command in container
execute_in_container() {
    local container="$1"
    local command
    
    read -p "Enter command to execute: " command
    print_info "Executing: ${command}"
    
    run_remote_command "cd ${DOCKER_DIR} && docker compose exec ${container} ${command}"
}

# Rebuild all containers
rebuild_containers() {
    show_header
    print_section_header "Container Rebuild"
    
    print_info "This will rebuild all the Docker containers."
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot rebuild containers in local mode"
        press_enter_to_continue
        show_container_menu
        return
    fi
    
    # Check if a rebuild was done in the last 5 minutes
    local rebuild_timestamp_file="/tmp/homelab_last_rebuild"
    local current_time=$(date +%s)
    local skip_confirmations=false
    
    if [ -f "$rebuild_timestamp_file" ]; then
        local last_rebuild_time=$(cat "$rebuild_timestamp_file")
        local time_diff=$((current_time - last_rebuild_time))
        
        # If less than 5 minutes (300 seconds) since last rebuild
        if [ $time_diff -lt 300 ]; then
            print_warning "A rebuild was performed in the last 5 minutes ($(( time_diff / 60 )) minutes ago)"
            if get_yes_no "Skip confirmations and perform quick rebuild?"; then
                skip_confirmations=true
            fi
        fi
    fi
    
    local delete_data=false
    
    if [ "$skip_confirmations" = false ]; then
        # CRITICAL WARNING about data deletion
        print_error "⚠️ WARNING: Deleting volumes will PERMANENTLY ERASE ALL DATABASE DATA ⚠️"
        print_error "This action cannot be undone unless you have a backup!"
        
        # Require explicit confirmation with "DELETE" to proceed with data deletion
        if get_confirmed_input "Are you absolutely sure you want to delete all data? This will ERASE YOUR DATABASE!" "DELETE"; then
            delete_data=true
            
            # Double-check with a different confirmation word for extra safety
            if ! get_confirmed_input "Final verification - type 'CONFIRM-DELETION' to proceed with data deletion:" "CONFIRM-DELETION"; then
                print_info "Data deletion cancelled"
                delete_data=false
            fi
        else
            delete_data=false
        fi
        
        if [ "$delete_data" = true ]; then
            # Recommend backup before proceeding
            if get_yes_no "Would you like to create a backup before deleting all data?"; then
                backup_database
            fi
        fi
    else
        # With skip_confirmations, default to safe rebuild without data deletion
        print_info "Using quick rebuild WITHOUT data deletion"
        delete_data=false
    fi
    
    # Save current timestamp for future reference
    echo "$current_time" > "$rebuild_timestamp_file"
    
    if [ "$delete_data" = true ]; then
        print_warning "Performing FULL rebuild WITH data deletion..."
        run_remote_command "cd ${DOCKER_DIR} && docker compose down -v && docker compose build --no-cache && docker compose up -d"
    else
        print_info "Performing rebuild WITHOUT data deletion..."
        # Use "stop" instead of "down" to ensure volumes are not touched
        run_remote_command "cd ${DOCKER_DIR} && docker compose stop && docker compose rm -f && docker compose build --no-cache && docker compose up -d"
    fi
    
    print_success "Rebuild completed successfully!"
    press_enter_to_continue
    show_container_menu
} 