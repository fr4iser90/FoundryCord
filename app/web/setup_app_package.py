#!/usr/bin/env python3
import os
import sys
import shutil

def setup_app_package():
    """
    Sets up the app package structure to allow imports in both
    app.web and app.bot formats while working with Docker volumes.
    """
    print("Setting up app package structure...")
    
    # Create the app directory if it doesn't exist
    if not os.path.exists('/app/app'):
        os.makedirs('/app/app', exist_ok=True)
        print("Created /app/app directory")
    
    # Create __init__.py files at various levels to make Python treat directories as packages
    init_paths = [
        '/app/__init__.py', 
        '/app/app/__init__.py',
        '/app/app/web/__init__.py',
        '/app/app/bot/__init__.py'
    ]
    
    for init_path in init_paths:
        dir_path = os.path.dirname(init_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory {dir_path}")
        
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write('# Package initialization file\n')
            print(f"Created {init_path}")
    
    # Ensure bot and web directories exist at the root level
    for dir_name in ['bot', 'web']:
        if not os.path.exists(f'/app/{dir_name}'):
            os.makedirs(f'/app/{dir_name}', exist_ok=True)
            print(f"Created /app/{dir_name} directory")

    # Make sure we have __init__.py in /app/bot and /app/web too
    for dir_name in ['bot', 'web']:
        init_file = f'/app/{dir_name}/__init__.py'
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Package initialization file\n')
            print(f"Created {init_file}")
    
    # Create symbolic links if they don't exist
    symlinks = [
        ('/app/bot', '/app/app/bot'),
        ('/app/web', '/app/app/web')
    ]
    
    for src, dst in symlinks:
        # Remove existing destination if it's not a proper symlink
        if os.path.exists(dst) and not os.path.islink(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
            print(f"Removed existing {dst}")
        
        # Create symbolic link if it doesn't exist
        if not os.path.exists(dst):
            # Make sure source exists before creating symlink
            if os.path.exists(src):
                os.symlink(src, dst)
                print(f"Created symbolic link from {src} to {dst}")
            else:
                print(f"Warning: Source directory {src} does not exist")
    
    # Add app directory to Python path
    app_path = '/app'
    if app_path not in sys.path:
        sys.path.insert(0, app_path)
        print(f"Added {app_path} to Python path")
    
    print("App package setup complete")
    
    # Show Python path
    print("=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    print()

if __name__ == "__main__":
    setup_app_package() 