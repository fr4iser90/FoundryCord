#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Database Menu
# =======================================================

# Show database menu
show_database_menu() {
    show_header
    
    print_section_header "Database Tools"
    print_menu_item "1" "Apply Alembic Migration"
    print_menu_item "2" "Update Remote Database"
    print_menu_item "3" "Backup Database"
    print_menu_item "4" "Restore Database"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case "$choice" in
        1) 
            run_alembic_migration
            press_enter_to_continue
            show_database_menu
            ;;
        2) 
            update_remote_database
            press_enter_to_continue
            show_database_menu
            ;;
        3)
            backup_database
            press_enter_to_continue
            show_database_menu
            ;;
        4)
            restore_database
            press_enter_to_continue
            show_database_menu
            ;;
        0) show_main_menu ;;
        *) 
            print_error "Invalid option!"
            sleep 1
            show_database_menu
            ;;
    esac
} 