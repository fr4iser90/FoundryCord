#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Container Menu
# =======================================================

# Show container management menu
show_container_menu() {
    # Get list of available containers
    load_available_containers
    
    show_header
    print_section_header "Container Management"
    
    print_menu_item "1" "Start All Containers"
    print_menu_item "2" "Stop All Containers"
    print_menu_item "3" "Restart All Containers"
    print_menu_item "4" "Rebuild All Containers"
    print_menu_item "5" "Show Container Status"
    echo ""
    print_section_header "Individual Container Management"
    
    # Show numbered options for each container
    local counter=6
    for container in "${CONTAINER_ACTIONS[@]}"; do
        print_menu_item "$counter" "Manage ${container} container"
        ((counter++))
    done
    
    echo ""
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) manage_all_containers "start" ;;
        2) manage_all_containers "stop" ;;
        3) manage_all_containers "restart" ;;
        4) rebuild_containers ;;
        5) show_container_status ;;
        0) show_main_menu ;;
        *)
            # Check if container option was selected
            local container_index=$((choice - 6))
            if [ "$container_index" -ge 0 ] && [ "$container_index" -lt "${#CONTAINER_ACTIONS[@]}" ]; then
                local selected_container="${CONTAINER_ACTIONS[$container_index]}"
                manage_single_container "$selected_container"
            else
                print_error "Invalid option!"
                sleep 1
                show_container_menu
            fi
            ;;
    esac
}

# Show individual container management menu
manage_single_container() {
    local container="$1"
    show_header
    
    print_section_header "Managing ${container} container"
    print_menu_item "1" "Start container"
    print_menu_item "2" "Stop container"
    print_menu_item "3" "Restart container"
    print_menu_item "4" "View logs"
    print_menu_item "5" "Rebuild container"
    print_menu_item "6" "Execute command in container"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot manage containers in local mode"
        press_enter_to_continue
        show_container_menu
        return
    fi
    
    case "$choice" in
        1) container_action "$container" "start" ;;
        2) container_action "$container" "stop" ;;
        3) container_action "$container" "restart" ;;
        4) view_container_logs "$container" ;;
        5) rebuild_single_container "$container" ;;
        6) execute_in_container "$container" ;;
        0) show_container_menu; return ;;
        *) print_error "Invalid option" ;;
    esac
    
    press_enter_to_continue
    manage_single_container "$container"
} 