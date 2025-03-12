"""
Diagnostic script to check module availability and print the Python path.
"""
import sys
import os

def check_module(module_name):
    try:
        __import__(module_name)
        print(f"✅ Module '{module_name}' is available")
        return True
    except ImportError as e:
        print(f"❌ Module '{module_name}' is not available: {e}")
        return False

def main():
    print("=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    
    print("\n=== Module Checks ===")
    modules_to_check = [
        "fastapi", 
        "interfaces",  # The problematic module
        "app.bot.interfaces" if "app.bot" in sys.modules else "app.bot.interfaces (alternative path)",
        "bot.interfaces" if "bot" in sys.modules else "bot.interfaces (alternative path)"
    ]
    
    for module in modules_to_check:
        check_module(module)
    
    print("\n=== Directory Contents ===")
    dirs_to_check = ["/app", "/app/web", "/app/bot"]
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"Contents of {dir_path}:")
            for item in os.listdir(dir_path):
                print(f"  - {item}")
        else:
            print(f"Directory {dir_path} does not exist")

if __name__ == "__main__":
    main() 