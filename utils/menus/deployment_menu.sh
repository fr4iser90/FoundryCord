#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Deployment Menu
# =======================================================

# Show deployment menu
show_deployment_menu() {
    show_header
    print_section_header "Deployment Menu"
    
    print_menu_item "1" "Quick Deploy - Deploy with .env preservation (SAFE, preserves database)"
    print_menu_item "2" "Quick Deploy with Auto-Start (preserves data, auto-builds AND auto-starts)"
    print_menu_item "3" "Partial Deploy - Rebuild containers only (SAFE, preserves database)"
    print_menu_item "4" "Check Services - Verify running services"
    print_menu_item "5" "Update Docker Configuration - Update Docker files"
    print_menu_item "6" "Check Docker Files - Verify Docker configuration"
    print_menu_item "7" "Configure Auto-start Settings"
    echo ""
    print_section_header "⚠️ DANGER ZONE - DATA LOSS OPTIONS ⚠️"
    print_menu_item "8" "FULL RESET DEPLOY - Complete deployment with database reset (WILL DELETE ALL DATA)"
    print_menu_item "9" "FULL RESET + VOLUME REMOVAL - Complete reset including all volumes (WILL DELETE EVERYTHING)"
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
            run_quick_deploy_with_auto_start
            press_enter_to_continue
            show_deployment_menu
            ;;
        3)
            run_partial_deploy
            press_enter_to_continue
            show_deployment_menu
            ;;
        4)
            check_services
            press_enter_to_continue
            show_deployment_menu
            ;;
        5)
            update_docker_config
            press_enter_to_continue
            show_deployment_menu
            ;;
        6)
            check_docker_files
            press_enter_to_continue
            show_deployment_menu
            ;;
        7)
            show_auto_start_menu
            ;;
        8)
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
        9)
            # Extra warning for volume-destroying option
            clear
            print_section_header "⚠️ EXTREME DANGER: FULL RESET WITH VOLUME REMOVAL ⚠️"
            print_error "This will COMPLETELY ERASE your database AND ALL VOLUMES!"
            print_error "This action CANNOT be undone unless you have a backup!"
            echo ""
            
            if get_confirmed_input "Are you absolutely sure you want to DELETE ALL DATA AND VOLUMES?" "DELETE-ALL-DATA-AND-VOLUMES"; then
                if get_yes_no "Would you like to create a backup before proceeding?"; then
                    backup_database
                fi
                export REMOVE_VOLUMES=true
                run_full_reset_deploy
                export REMOVE_VOLUMES=false
            else
                print_info "Full reset with volume removal cancelled"
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