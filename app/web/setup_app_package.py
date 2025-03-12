"""
Helper script to create the necessary package structure for app.bot imports.
"""
import os
import sys

def setup_app_package():
    """Create the necessary directory structure and __init__.py files"""
    # Create app directory if it doesn't exist
    app_dir = "/app/app"
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        print(f"Created directory: {app_dir}")
    
    # Create app/__init__.py if it doesn't exist
    app_init = os.path.join(app_dir, "__init__.py")
    if not os.path.exists(app_init):
        with open(app_init, "w") as f:
            f.write('"""App package"""')
        print(f"Created file: {app_init}")
    
    # Create symlink from /app/bot to /app/app/bot if it doesn't exist
    app_bot_dir = os.path.join(app_dir, "bot")
    if not os.path.exists(app_bot_dir):
        try:
            os.symlink("/app/bot", app_bot_dir)
            print(f"Created symlink: /app/bot -> {app_bot_dir}")
        except OSError as e:
            print(f"Failed to create symlink: {e}")
    
    print("App package setup complete")

if __name__ == "__main__":
    setup_app_package() 