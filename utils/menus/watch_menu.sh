#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Watch Menu
# =======================================================

# Show watch menu for real-time monitoring
show_watch_menu() {
    show_header
    print_section_header "Real-time Monitoring"
    
    # Get list of available containers
    load_available_containers
    
    print_menu_item "1" "Watch All Services"
    print_menu_item "2" "Watch Bot Only"
    print_menu_item "3" "Watch Database Only"
    print_menu_item "4" "Watch System Resources"
    print_menu_item "5" "Custom Service Selection"
    
    echo ""
    print_menu_item "6" "Interactive Dashboard Mode (requires tmux)"
    print_back_option
    echo ""
    
    local choice=$(get_numeric_input "Select an option: ")
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot monitor services in local mode"
        press_enter_to_continue
        show_main_menu
        return
    fi
    
    case $choice in
        1)
            # Watch all services
            print_info "Watching all services. Press Ctrl+C to stop..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50"
            ;;
        2)
            # Watch bot only
            print_info "Watching bot service. Press Ctrl+C to stop..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50 bot"
            ;;
        3)
            # Watch database only
            print_info "Watching database service. Press Ctrl+C to stop..."
            run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50 postgres"
            ;;
        4)
            # Watch system resources
            print_info "Watching system resources. Press Ctrl+C to stop..."
            run_remote_command "watch -n 1 'echo \"=== DOCKER STATS ===\" && docker stats --no-stream && echo \"=== SYSTEM RESOURCES ===\" && free -h && df -h | grep -v tmpfs'"
            ;;
        5)
            # Custom service selection
            show_header
            print_section_header "Select Services to Monitor"
            
            # Show available services
            local counter=1
            local selected_services=""
            
            for container in "${CONTAINER_ACTIONS[@]}"; do
                print_menu_item "$counter" "$container"
                ((counter++))
            done
            
            echo ""
            echo "Enter service numbers separated by commas (e.g., 1,3,4):"
            read -p "> " service_numbers
            
            # Parse service numbers
            IFS=',' read -ra NUMS <<< "$service_numbers"
            for num in "${NUMS[@]}"; do
                num=$(echo "$num" | tr -d ' ')
                if [[ $num =~ ^[0-9]+$ ]]; then
                    local index=$((num - 1))
                    if [ $index -ge 0 ] && [ $index -lt ${#CONTAINER_ACTIONS[@]} ]; then
                        if [ -z "$selected_services" ]; then
                            selected_services="${CONTAINER_ACTIONS[$index]}"
                        else
                            selected_services="$selected_services ${CONTAINER_ACTIONS[$index]}"
                        fi
                    fi
                fi
            done
            
            if [ -n "$selected_services" ]; then
                print_info "Watching services: $selected_services. Press Ctrl+C to stop..."
                run_remote_command "cd ${DOCKER_DIR} && docker compose logs -f --tail=50 $selected_services"
            else
                print_error "No services selected"
                press_enter_to_continue
                show_watch_menu
                return
            fi
            ;;
        6)
            # Interactive Dashboard Mode
            if ! run_remote_command "command -v tmux" "silent" | grep -q tmux; then
                print_error "tmux is not installed on the remote server."
                print_info "Please install tmux for dashboard mode."
                press_enter_to_continue
                show_watch_menu
                return
            fi
            
            print_info "Starting interactive dashboard. Press Ctrl+B then D to detach..."
            
            # Create a tmux session with multiple panes
            run_remote_command "tmux new-session -d -s homelab-dashboard 'docker stats' \\; \
                split-window -v 'cd ${DOCKER_DIR} && docker compose logs -f --tail=20 bot' \\; \
                split-window -h 'cd ${DOCKER_DIR} && docker compose logs -f --tail=20 postgres' \\; \
                select-pane -t 0 \\; \
                split-window -h 'watch -n 5 \"free -h; echo; df -h | grep -v tmpfs\"' \\; \
                attach-session -d"
            ;;
        0)
            show_main_menu
            return
            ;;
        *)
            print_error "Invalid option!"
            press_enter_to_continue
            show_watch_menu
            ;;
    esac
    
    press_enter_to_continue
    show_watch_menu
} 