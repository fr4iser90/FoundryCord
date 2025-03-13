"""
Diagnostic script to check module availability and print the Python path.
"""
#!/usr/bin/env python3
import sys
import importlib

def check_module(module_name):
    """Check if a module can be imported and print the result"""
    try:
        __import__(module_name)
        print(f"✅ Module '{module_name}' is available")
        return True
    except ImportError as e:
        print(f"❌ Module '{module_name}' is not available: {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ Error checking module '{module_name}': {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to check required modules"""
    print("=== Module Checks ===")
    
    # List of modules to check
    modules = [
        "fastapi",            # Web framework
        "interfaces",         # Web interface modules
        "bot.interfaces (alternative path)"  # Bot interface modules
    ]
    
    # Check each module
    for module in modules:
        if " " in module:
            # This is a description, extract the actual module name
            parts = module.split(" ", 1)
            module_name = parts[0]
        else:
            module_name = module
        
        check_module(module_name)
    
    # Add additional path information
    print("=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    print()

if __name__ == "__main__":
    main() 