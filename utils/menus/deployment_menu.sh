#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Menu
# =======================================================

# Show deployment menu
show_deployment_menu() {
    show_header
    print_section_header "Deployment Menu"
    
    print_menu_item "1" "Quick Deploy - Deploy with direct .env file copying (SAFE, preserves database)"
    print_menu_item "2" "Partial Deploy - Rebuild containers only (SAFE, preserves database)"
    print_menu_item "3" "Check Services - Verify running services"
    print_menu_item "4" "Update Docker Configuration - Update Docker files"
    print_menu_item "5" "Check Docker Files - Verify Docker configuration"
    echo ""
    print_section_header "⚠️ DANGER ZONE - DATA LOSS OPTIONS ⚠️"
    print_menu_item "6" "FULL RESET DEPLOY - Complete deployment with database reset (WILL DELETE ALL DATA)"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case $choice in
        1)
            run_quick_deploy
            press_enter_to_continue
            show_deployment_menu
            ;;
        2)
            run_partial_deploy
            press_enter_to_continue
            show_deployment_menu
            ;;
        3)
            check_services
            press_enter_to_continue
            show_deployment_menu
            ;;
        4)
            update_docker_config
            press_enter_to_continue
            show_deployment_menu
            ;;
        5)
            check_docker_files
            press_enter_to_continue
            show_deployment_menu
            ;;
        6)
            # Extra warning for data-destroying option
            clear
            print_section_header "⚠️ DANGER: FULL RESET DEPLOYMENT ⚠️"
            print_error "This will COMPLETELY ERASE your database and all data!"
            print_error "This action CANNOT be undone unless you have a backup!"
            echo ""
            
            if get_confirmed_input "Are you absolutely sure you want to DELETE ALL DATA?" "DELETE-ALL-DATA"; then
                if get_yes_no "Would you like to create a backup before proceeding?"; then
                    backup_database
                fi
                run_full_reset_deploy
            else
                print_info "Full reset deployment cancelled"
            fi
            
            press_enter_to_continue
            show_deployment_menu
            ;;
        0)
            show_main_menu
            ;;
        *)
            print_error "Invalid option"
            press_enter_to_continue
            show_deployment_menu
            ;;
    esac
} 