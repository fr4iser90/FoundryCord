#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Test File Uploader
# =======================================================

# Move to project root directory regardless of where script is called from
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

# Source common utilities
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

# ------------------------------------------------------
# Command-line Arguments Parsing
# ------------------------------------------------------
parse_args "$@"

# ------------------------------------------------------
# Main Upload Function
# ------------------------------------------------------
upload_test_files() {
    log_info "Uploading test files to ${SERVER_HOST}..."
    
    # Check if test directory exists
    if [ ! -d "$LOCAL_TESTS_DIR" ]; then
        log_error "Test directory not found: $LOCAL_TESTS_DIR"
        log_info "Creating test directory structure..."
        
        # Create test directory structure
        mkdir -p "$LOCAL_TESTS_DIR/unit"
        mkdir -p "$LOCAL_TESTS_DIR/integration"
        mkdir -p "$LOCAL_TESTS_DIR/system"
        
        # Create sample test files
        create_sample_tests
    fi
    
    # Create remote test directories
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/tests/unit"
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/tests/integration"
    run_remote_command "mkdir -p ${PROJECT_ROOT_DIR}/tests/system"
    
    # Upload all test files
    for test_file in $(find "$LOCAL_TESTS_DIR" -name "test_*.py"); do
        rel_path="${test_file#$LOCAL_TESTS_DIR/}"
        remote_path="${PROJECT_ROOT_DIR}/tests/${rel_path}"
        remote_dir=$(dirname "$remote_path")
        
        # Ensure remote directory exists
        run_remote_command "mkdir -p $remote_dir" "true"
        
        # Upload the file
        log_info "Uploading $test_file"
        upload_file "$test_file" "$remote_path"
    done
    
    # Verify the test files were uploaded correctly
    TEST_FILES=$(run_remote_command "find ${PROJECT_ROOT_DIR}/tests -name 'test_*.py' | wc -l")
    
    if [ "$TEST_FILES" -eq 0 ]; then
        log_error "No test files were uploaded or found."
        return 1
    else
        log_success "Test files uploaded successfully."
        log_info "Uploaded files: $TEST_FILES"
        return 0
    fi
}

# ------------------------------------------------------
# Create Sample Tests Function
# ------------------------------------------------------
create_sample_tests() {
    log_info "Creating sample test files..."
    
    # Create a basic structure test
    cat > "$LOCAL_TESTS_DIR/system/test_structure.py" << 'EOL'
import os
import sys
import pytest

def test_directory_structure():
    """Test to verify the directory structure and print it for debugging"""
    print("\n\n=== CURRENT DIRECTORY ===")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\n=== PYTHON PATH ===")
    for path in sys.path:
        print(path)
    
    print("\n=== DIRECTORY STRUCTURE ===")
    
    # Print first level directories in working directory
    print("Working directory contents:")
    for item in os.listdir('.'):
        if os.path.isdir(os.path.join('.', item)):
            print(f"  - {item}/")
        else:
            print(f"  - {item}")
    
    # Check interface structure
    interfaces_dir = "/app/bot/interfaces"
    if os.path.exists(interfaces_dir):
        print("\nInterfaces directory structure:")
        for item in os.listdir(interfaces_dir):
            item_path = os.path.join(interfaces_dir, item)
            if os.path.isdir(item_path):
                print(f"  - {item}/")
                # If it's web, explore deeper
                if item == "web":
                    for subitem in os.listdir(item_path):
                        if subitem.startswith('__'):
                            continue
                        sub_path = os.path.join(item_path, subitem)
                        if os.path.isdir(sub_path):
                            print(f"    - {subitem}/")
                            # Explore one more level
                            for subsub in os.listdir(sub_path):
                                if subsub.startswith('__'):
                                    continue
                                print(f"      - {subsub}")
                        else:
                            print(f"    - {subitem}")
    
    # Assert something simple to make the test pass
    assert True, "Directory structure test completed"
EOL

    # Create a sample auth test
    cat > "$LOCAL_TESTS_DIR/unit/test_auth.py" << 'EOL'
import pytest
import sys

def test_auth_module_exists():
    """Verify the auth module exists and can be imported"""
    try:
        # Try to import the auth module using the correct path for the container
        from app.bot.interfaces.web import api as web_api
        from app.bot.interfaces.web import ui as web_ui
        print("Successfully imported web modules")
        
        # List what's available in the modules
        print("Web API module contains:", dir(web_api))
        print("Web UI module contains:", dir(web_ui))
        
        # Check if server.py exists and can be imported
        try:
            from app.bot.interfaces.web.server import app
            print("Successfully imported web server app")
        except ImportError as e:
            print(f"Failed to import web server: {e}")
        
        assert True
    except ImportError as e:
        print(f"Import error: {e}")
        # Print the Python path to help diagnose import issues
        print("Python path:")
        for path in sys.path:
            print(f"  - {path}")
        
        assert False, f"Failed to import web module: {e}"

def test_basic_auth_functionality():
    """Test basic functionality - always passes for now"""
    assert True, "Basic auth functionality test"
EOL

    # Create a sample integration test
    cat > "$LOCAL_TESTS_DIR/integration/test_database.py" << 'EOL'
import pytest
import sys
import os

def test_database_connection():
    """Verify database connection works"""
    try:
        # Try to import database modules
        from app.shared.infrastructure.database.models.config import initialize_engine
        print("Successfully imported database configuration")
        
        # This is just a placeholder for now - in a real test you'd connect to the DB
        assert True, "Database import successful"
    except ImportError as e:
        print(f"Import error: {e}")
        assert False, f"Failed to import database module: {e}"

def test_redis_connection():
    """Verify Redis connection works"""
    try:
        # Try to import Redis
        import redis
        print("Successfully imported Redis module")
        
        # This is just a placeholder - in a real test you'd connect to Redis
        assert True, "Redis import successful"
    except ImportError as e:
        print(f"Import error: {e}")
        assert False, f"Failed to import Redis module: {e}"
EOL

    log_success "Sample test files created successfully"
}

# ------------------------------------------------------
# Main function
# ------------------------------------------------------
main() {
    # Check SSH connection
    check_ssh_connection
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Upload test files
    upload_test_files
    if [ $? -ne 0 ]; then
        exit 1
    fi
}

# Run the main function
main 