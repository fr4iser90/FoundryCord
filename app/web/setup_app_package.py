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
    
    # Create symbolic links if they don't exist
    symlinks = [
        ('/app/bot', '/app/app/bot'),
        ('/app/web', '/app/app/web'),
        ('/app/shared', '/app/app/shared'),
        ('/app/database', '/app/app/database')
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
        if not os.path.exists(dst) and os.path.exists(src):
            os.symlink(src, dst)
            print(f"Created symbolic link from {src} to {dst}")


if __name__ == "__main__":
    setup_app_package() 