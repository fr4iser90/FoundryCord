#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Auto-start Menu
# =======================================================

# Show auto-start menu
show_auto_start_menu() {
    show_header
    print_section_header "Auto-start Configuration"
    
    # Show current settings
    echo -e "Current auto-start settings:"
    echo -e "  Auto-start enabled: ${GREEN}${AUTO_START}${NC}"
    echo -e "  Services to start: ${GREEN}${AUTO_START_SERVICES}${NC}"
    echo -e "  Wait time: ${GREEN}${AUTO_START_WAIT}${NC} seconds"
    echo -e "  Auto-build enabled: ${GREEN}${AUTO_BUILD_ENABLED}${NC}"
    echo -e "  Feedback level: ${GREEN}${AUTO_START_FEEDBACK}${NC}"
    echo ""
    
    print_menu_item "1" "Enable/disable auto-start"
    print_menu_item "2" "Configure services to auto-start"
    print_menu_item "3" "Set wait time after startup"
    print_menu_item "4" "Enable/disable auto-build"
    print_menu_item "5" "Set feedback level"
    print_menu_item "6" "Save configuration"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    case $choice in
        1)
            if [ "${AUTO_START}" = "true" ]; then
                AUTO_START="false"
                print_info "Auto-start disabled"
            else
                AUTO_START="true"
                print_info "Auto-start enabled"
            fi
            press_enter_to_continue
            show_auto_start_menu
            ;;
        2)
            echo "Select services to auto-start:"
            echo "1. All services"
            echo "2. No services"
            echo "3. Custom selection"
            local service_choice=$(get_numeric_input "Select an option: ")
            
            case $service_choice in
                1)
                    AUTO_START_SERVICES="all"
                    ;;
                2)
                    AUTO_START_SERVICES="none"
                    ;;
                3)
                    # Get available services
                    load_available_containers
                    
                    echo "Available services:"
                    local counter=1
                    for container in "${CONTAINER_ACTIONS[@]}"; do
                        echo "${counter}. $container"
                        ((counter++))
                    done
                    
                    echo "Enter service numbers separated by commas:"
                    read -p "> " service_numbers
                    
                    # Convert numbers to service names
                    local selected_services=""
                    IFS=',' read -ra NUMS <<< "$service_numbers"
                    for num in "${NUMS[@]}"; do
                        num=$(echo "$num" | tr -d ' ')
                        if [[ $num =~ ^[0-9]+$ ]]; then
                            local index=$((num - 1))
                            if [ $index -ge 0 ] && [ $index -lt ${#CONTAINER_ACTIONS[@]} ]; then
                                if [ -z "$selected_services" ]; then
                                    selected_services="${CONTAINER_ACTIONS[$index]}"
                                else
                                    selected_services="$selected_services,${CONTAINER_ACTIONS[$index]}"
                                fi
                            fi
                        fi
                    done
                    
                    if [ -n "$selected_services" ]; then
                        AUTO_START_SERVICES="$selected_services"
                    else
                        print_error "No valid services selected"
                        AUTO_START_SERVICES="none"
                    fi
                    ;;
            esac
            
            print_info "Services set to: ${AUTO_START_SERVICES}"
            press_enter_to_continue
            show_auto_start_menu
            ;;
        3)
            AUTO_START_WAIT=$(get_numeric_input "Enter wait time in seconds: ")
            print_info "Wait time set to ${AUTO_START_WAIT} seconds"
            press_enter_to_continue
            show_auto_start_menu
            ;;
        4)
            if [ "${AUTO_BUILD_ENABLED}" = "true" ]; then
                AUTO_BUILD_ENABLED="false"
                print_info "Auto-build disabled"
            else
                AUTO_BUILD_ENABLED="true"
                print_info "Auto-build enabled"
            fi
            press_enter_to_continue
            show_auto_start_menu
            ;;
        5)
            echo "Select feedback level:"
            echo "1. None - No feedback during auto-start"
            echo "2. Minimal - Basic status information"
            echo "3. Verbose - Detailed logs and status"
            local feedback_choice=$(get_numeric_input "Select an option: ")
            
            case $feedback_choice in
                1) AUTO_START_FEEDBACK="none" ;;
                2) AUTO_START_FEEDBACK="minimal" ;;
                3) AUTO_START_FEEDBACK="verbose" ;;
                *) print_error "Invalid option" ;;
            esac
            
            print_info "Feedback level set to: ${AUTO_START_FEEDBACK}"
            press_enter_to_continue
            show_auto_start_menu
            ;;
        6)
            save_auto_start_config "${AUTO_START}" "${AUTO_START_SERVICES}" "${AUTO_START_FEEDBACK}"
            press_enter_to_continue
            show_auto_start_menu
            ;;
        0)
            show_main_menu
            ;;
        *)
            print_error "Invalid option"
            press_enter_to_continue
            show_auto_start_menu
            ;;
    esac
} 