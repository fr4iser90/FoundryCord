#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Logs Menu
# =======================================================

# Show logs menu
show_logs_menu() {
    show_header
    
    print_section_header "Logs Menu"
    print_menu_item "1" "View Bot Logs"
    print_menu_item "2" "View Database Logs"
    print_menu_item "3" "View Redis Logs"
    print_menu_item "4" "View Web Logs"
    print_menu_item "5" "View System Logs"
    print_menu_item "6" "View Docker Logs"
    print_menu_item "7" "Download All Logs"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) view_bot_logs ;;
        2) view_db_logs ;;
        3) view_redis_logs ;;
        4) view_web_logs ;;
        5) view_system_logs ;;
        6) view_docker_logs ;;
        7) download_logs ;;
        0) show_main_menu ;;
        *) 
            print_error "Invalid option!"
            sleep 1
            show_logs_menu
            ;;
    esac
} 