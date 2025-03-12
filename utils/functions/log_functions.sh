#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Log Functions
# =======================================================

# View bot logs
view_bot_logs() {
    clear
    print_section_header "Bot Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        local lines=$(get_string_input "Number of log lines to show" "100")
        local follow=false
        
        if get_yes_no "Follow logs in real time?"; then
            follow=true
        fi
        
        if [ "$follow" = true ]; then
            print_info "Viewing bot logs (Press Ctrl+C to exit)..."
            run_remote_command "docker logs --tail=${lines} -f ${BOT_CONTAINER}"
        else
            print_info "Viewing last ${lines} lines of bot logs..."
            run_remote_command "docker logs --tail=${lines} ${BOT_CONTAINER}"
        fi
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# View database logs
view_db_logs() {
    clear
    print_section_header "Database Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        local lines=$(get_string_input "Number of log lines to show" "100")
        local follow=false
        
        if get_yes_no "Follow logs in real time?"; then
            follow=true
        fi
        
        if [ "$follow" = true ]; then
            print_info "Viewing database logs (Press Ctrl+C to exit)..."
            run_remote_command "docker logs --tail=${lines} -f ${POSTGRES_CONTAINER}"
        else
            print_info "Viewing last ${lines} lines of database logs..."
            run_remote_command "docker logs --tail=${lines} ${POSTGRES_CONTAINER}"
        fi
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# View web logs
view_web_logs() {
    clear
    print_section_header "Web Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        # Check if web container exists
        if ! run_remote_command "docker ps -q -f name=${WEB_CONTAINER}" "silent" | grep -q .; then
            print_error "Web container not found or not running"
            press_enter_to_continue
            show_logs_menu
            return
        fi
        
        local lines=$(get_string_input "Number of log lines to show" "100")
        local follow=false
        
        if get_yes_no "Follow logs in real time?"; then
            follow=true
        fi
        
        if [ "$follow" = true ]; then
            print_info "Viewing web logs (Press Ctrl+C to exit)..."
            run_remote_command "docker logs --tail=${lines} -f ${WEB_CONTAINER}"
        else
            print_info "Viewing last ${lines} lines of web logs..."
            run_remote_command "docker logs --tail=${lines} ${WEB_CONTAINER}"
        fi
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# View redis logs
view_redis_logs() {
    clear
    print_section_header "Redis Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        local lines=$(get_string_input "Number of log lines to show" "100")
        local follow=false
        
        if get_yes_no "Follow logs in real time?"; then
            follow=true
        fi
        
        if [ "$follow" = true ]; then
            print_info "Viewing Redis logs (Press Ctrl+C to exit)..."
            run_remote_command "docker logs --tail=${lines} -f ${REDIS_CONTAINER}"
        else
            print_info "Viewing last ${lines} lines of Redis logs..."
            run_remote_command "docker logs --tail=${lines} ${REDIS_CONTAINER}"
        fi
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# View system logs
view_system_logs() {
    clear
    print_section_header "System Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        print_info "Viewing system journal logs..."
        run_remote_command "sudo journalctl -n 100 --no-pager"
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# View Docker logs
view_docker_logs() {
    clear
    print_section_header "Docker Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot view logs in local mode"
    else
        print_info "Viewing Docker daemon logs..."
        run_remote_command "sudo journalctl -u docker -n 100 --no-pager"
    fi
    
    press_enter_to_continue
    show_logs_menu
}

# Download logs
download_logs() {
    clear
    print_section_header "Download Logs"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot download logs in local mode"
        press_enter_to_continue
        show_logs_menu
        return
    fi
    
    # Create local logs directory if it doesn't exist
    mkdir -p "./logs"
    
    # Get timestamp for unique filenames
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    print_info "Downloading logs..."
    
    # Bot logs
    print_info "Downloading bot logs..."
    run_remote_command "docker logs ${BOT_CONTAINER} > /tmp/bot_${timestamp}.log"
    scp "${SERVER_USER}@${SERVER_HOST}:/tmp/bot_${timestamp}.log" "./logs/"
    
    # Database logs
    print_info "Downloading database logs..."
    run_remote_command "docker logs ${POSTGRES_CONTAINER} > /tmp/db_${timestamp}.log"
    scp "${SERVER_USER}@${SERVER_HOST}:/tmp/db_${timestamp}.log" "./logs/"
    
    # Redis logs
    print_info "Downloading Redis logs..."
    run_remote_command "docker logs ${REDIS_CONTAINER} > /tmp/redis_${timestamp}.log"
    scp "${SERVER_USER}@${SERVER_HOST}:/tmp/redis_${timestamp}.log" "./logs/"
    
    # Web logs (if container exists)
    if run_remote_command "docker ps -q -f name=${WEB_CONTAINER}" "silent" | grep -q .; then
        print_info "Downloading web logs..."
        run_remote_command "docker logs ${WEB_CONTAINER} > /tmp/web_${timestamp}.log"
        scp "${SERVER_USER}@${SERVER_HOST}:/tmp/web_${timestamp}.log" "./logs/"
    fi
    
    print_success "Logs downloaded to ./logs/ directory"
    
    # Clean up remote temp files
    run_remote_command "rm /tmp/*_${timestamp}.log"
    
    press_enter_to_continue
    show_logs_menu
} 