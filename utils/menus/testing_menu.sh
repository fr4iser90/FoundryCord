#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Testing Menu
# =======================================================

# Show testing menu
show_testing_menu() {
    show_header
    
    print_section_header "Testing Tools"
    print_menu_item "1" "Run All Tests"
    print_menu_item "2" "Upload Tests"
    print_menu_item "3" "Test Server Environment"
    print_menu_item "4" "Check Remote Services"
    print_menu_item "5" "Initialize Test Environment"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) run_tests ;;
        2) upload_tests ;;
        3) test_server ;;
        4) check_remote_services ;;
        5) initialize_test_environment ;;
        0) show_main_menu ;;
        *) 
            print_error "Invalid option!"
            sleep 1
            show_testing_menu
            ;;
    esac
} 