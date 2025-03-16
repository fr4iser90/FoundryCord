import os
import sys
import pytest

def test_directory_structure():
    """Test to verify the directory structure and print it for debugging
    
    This test is a diagnostic tool that explores the project's directory structure
    and prints detailed information about:
    - Current working directory
    - Python path configuration
    - Directory hierarchy
    - Module loading status
    
    It's particularly useful for diagnosing import issues and configuration problems
    in different environments (development, testing, production).
    """
    print("\n\n=== CURRENT DIRECTORY ===")
    print(f"Current working directory: {os.getcwd()}")  # Show where Python thinks we are
    
    print("\n=== PYTHON PATH ===")
    for path in sys.path:
        print(path)  # List all directories where Python looks for modules
    
    print("\n=== DIRECTORY STRUCTURE ===")
    
    # Print first level directories in working directory
    print("Working directory contents:")
    for item in os.listdir('.'):
        if os.path.isdir(os.path.join('.', item)):
            print(f"  - {item}/")  # Directories end with /
        else:
            print(f"  - {item}")    # Files listed without trailing /
    
    # Check interface structure - critical for bot functionality
    interfaces_dir = "/app/bot/interfaces"
    if os.path.exists(interfaces_dir):
        print("\nInterfaces directory structure:")
        for item in os.listdir(interfaces_dir):
            item_path = os.path.join(interfaces_dir, item)
            if os.path.isdir(item_path):
                print(f"  - {item}/")
                # If it's web, explore deeper - web interface is particularly important
                if item == "web":
                    for subitem in os.listdir(item_path):
                        if subitem.startswith('__'):
                            continue  # Skip __pycache__ and similar dirs
                        sub_path = os.path.join(item_path, subitem)
                        if os.path.isdir(sub_path):
                            print(f"    - {subitem}/")
                            # Explore one more level for detailed structure
                            for subsub in os.listdir(sub_path):
                                if subsub.startswith('__'):
                                    continue  # Skip __pycache__ and similar dirs
                                print(f"      - {subsub}")
                        else:
                            print(f"    - {subitem}")
    
    # Try to list modules in sys.modules to see what's loaded
    # This helps diagnose import issues by showing what's actually been loaded
    print("\n=== LOADED MODULES ===")
    print("Number of loaded modules:", len(sys.modules))
    for module_name in sorted(sys.modules.keys()):
        # Filter to show only modules relevant to our application
        if 'app' in module_name or 'interface' in module_name or 'web' in module_name:
            print(f"Module: {module_name}")
    
    # Special check for server.py file which likely contains the web routes
    # This is important because the web interface is crucial for the dashboard
    server_path = "/app/bot/interfaces/web/server.py"
    if os.path.exists(server_path):
        print("\nFound server.py file, showing first 20 lines:")
        with open(server_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                print(f"{i+1}: {line.rstrip()}")
    
    # Assert something simple to make the test pass
    # The real value of this test is the diagnostic information it prints
    assert True, "Directory structure test completed" 