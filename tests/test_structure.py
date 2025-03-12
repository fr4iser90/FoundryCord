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
    
    # Try to list modules in sys.modules to see what's loaded
    print("\n=== LOADED MODULES ===")
    print("Number of loaded modules:", len(sys.modules))
    for module_name in sorted(sys.modules.keys()):
        if 'app' in module_name or 'interface' in module_name or 'web' in module_name:
            print(f"Module: {module_name}")
    
    # Special check for server.py file which likely contains the web routes
    server_path = "/app/bot/interfaces/web/server.py"
    if os.path.exists(server_path):
        print("\nFound server.py file, showing first 20 lines:")
        with open(server_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                print(f"{i+1}: {line.rstrip()}")
    
    # Assert something simple to make the test pass
    assert True, "Directory structure test completed" 