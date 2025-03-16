#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Testing Menu
# =======================================================

# Show testing menu
show_testing_menu() {
    while true; do
        show_header
        
        print_section_header "Testing Menu"
        
        print_menu_item "1" "Run All Tests"
        print_menu_item "2" "Run Unit Tests"
        print_menu_item "3" "Run Integration Tests"
        print_menu_item "4" "Run System Tests"
        print_menu_item "5" "Run Dashboard Tests"
        print_menu_item "6" "Run Dashboard Tests Only"
        print_menu_item "7" "Run Simple Tests (No Dependencies)"
        print_menu_item "8" "Show Test Results"
        print_menu_item "9" "Server Status Tests"
        print_menu_item "10" "Run Tests in Priority Order"
        print_menu_item "11" "Run Tests with Docker Test Container"
        
        print_back_option
        
        echo ""
        local choice
        choice=$(get_numeric_input "Enter your choice: ")
        
        case $choice in
            1)
                run_all_tests
                press_enter_to_continue
                ;;
            2)
                run_unit_tests
                press_enter_to_continue
                ;;
            3)
                run_integration_tests
                press_enter_to_continue
                ;;
            4)
                run_system_tests
                press_enter_to_continue
                ;;
            5)
                run_dashboard_tests
                press_enter_to_continue
                ;;
            6)
                run_dashboard_tests
                ;;
            7)
                run_simple_test
                ;;
            8) show_test_results ;;
            9) test_server ;;
            10)
                run_ordered_tests
                press_enter_to_continue
                ;;
            11)
                run_tests_with_docker_container "all"
                press_enter_to_continue
                ;;
            0) show_main_menu ;;
            *) 
                print_error "Invalid option!"
                sleep 1
                show_testing_menu
                ;;
        esac
    done
}

# Add this function to utils/menus/testing_menu.sh
show_test_results() {
    clear
    print_section_header "Test Results"
    
    # Create results directory if it doesn't exist
    mkdir -p "$LOCAL_GIT_DIR/test-results"
    
    # Check if we have any test results
    if [ ! "$(ls -A "$LOCAL_GIT_DIR/test-results/")" ]; then
        print_warning "No test results found in $LOCAL_GIT_DIR/test-results/"
        press_enter_to_continue
        return
    fi
    
    # Show the available results files
    echo "Available test results:"
    ls -1t "$LOCAL_GIT_DIR/test-results/" | nl
    
    # Ask user which file to view
    echo ""
    local choice=$(get_numeric_input "Enter the number of the file to view (0 to go back): ")
    
    if [ "$choice" = "0" ]; then
        return
    fi
    
    # Get the filename from the list
    local file=$(ls -1t "$LOCAL_GIT_DIR/test-results/" | sed -n "${choice}p")
    
    if [ -n "$file" ]; then
        clear
        print_section_header "Test Results: $file"
        cat "$LOCAL_GIT_DIR/test-results/$file"
        echo ""
        press_enter_to_continue
    else
        print_error "Invalid selection"
        sleep 1
    fi
} 