#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Development Menu
# =======================================================

# Show development menu
show_development_menu() {
    show_header
    
    print_section_header "Development Tools"
    print_menu_item "1" "Generate Encryption Keys (Python Nix Shell)"
    print_menu_item "2" "Initialize Test Environment"
    print_menu_item "3" "Update Utility Scripts"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) generate_encryption_keys ;;
        2) initialize_dev_environment ;;
        3) update_utility_scripts ;;
        0) show_main_menu ;;
        *) 
            print_error "Invalid option!"
            sleep 1
            show_development_menu
            ;;
    esac
} 