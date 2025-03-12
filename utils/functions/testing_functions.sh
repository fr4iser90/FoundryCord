#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Testing Functions
# =======================================================

# Run tests
run_tests() {
    clear
    print_section_header "Run Tests"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot run remote tests in local mode"
    else
        ./utils/testing/run_tests.sh
    fi
    
    press_enter_to_continue
    show_testing_menu
}

# Upload tests
upload_tests() {
    clear
    print_section_header "Upload Tests"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot upload tests in local mode"
    else
        ./utils/testing/upload_tests.sh
    fi
    
    press_enter_to_continue
    show_testing_menu
}

# Test server
test_server() {
    clear
    print_section_header "Test Server"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot test server in local mode"
    else
        ./utils/testing/test_server.sh
    fi
    
    press_enter_to_continue
    show_testing_menu
}

# Check remote services
check_remote_services() {
    clear
    print_section_header "Check Remote Services"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot check remote services in local mode"
    else
        ./utils/testing/check_remote_services.sh
    fi
    
    press_enter_to_continue
    show_testing_menu
}

# Initialize test environment
initialize_test_environment() {
    clear
    print_section_header "Initialize Test Environment"
    
    ./utils/testing/init_test_env.sh
    
    press_enter_to_continue
    show_testing_menu
} 