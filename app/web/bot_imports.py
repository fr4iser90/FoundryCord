"""
Bridge module to import bot modules correctly.
This file helps establish the proper import paths for bot components.
"""

import sys
import os
import importlib

# Add parent directory to PATH to allow imports from app.bot
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Also ensure the root directory is in path for absolute imports
root_dir = "/"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Try different import styles
BOT_IMPORTS_SUCCESS = False
bot_web_interface = None

# Check if required bot modules are present
def check_dependencies():
    """Check if required dependencies for bot modules are installed"""
    try:
        # Try to import nextcord directly
        import nextcord
        print("✅ Nextcord is available")
        return True
    except ImportError as e:
        print(f"❌ Nextcord is not available: {e}")
        return False

# Install dependencies if they're missing
def install_missing_dependencies():
    """Install missing dependencies required by the bot"""
    try:
        print("Installing missing dependencies...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nextcord", "discord.py"])
        return True
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
        return False

# Attempt to import bot modules with dependency check
def import_bot_modules():
    global BOT_IMPORTS_SUCCESS, bot_web_interface
    
    # First check if we have all dependencies
    if not check_dependencies():
        if not install_missing_dependencies():
            print("Could not import bot modules due to missing dependencies")
            return False
    
    # First attempt - absolute imports
    try:
        from app.bot.interfaces import web as bot_web_interface
        BOT_IMPORTS_SUCCESS = True
        print("Successfully imported bot interfaces using absolute import path")
        return True
    except ImportError as e:
        print(f"Warning: Failed to import bot interfaces using absolute path: {e}")
    
    # Second attempt - relative to /app
    try:
        from bot.interfaces import web as bot_web_interface
        BOT_IMPORTS_SUCCESS = True
        print("Successfully imported bot interfaces using relative import path")
        return True
    except ImportError as e:
        print(f"Warning: Failed to import bot interfaces using relative path: {e}")
    
    # Last attempt - direct path manipulation
    try:
        # Add the bot's interfaces directory directly to the path
        bot_interfaces_path = os.path.join(parent_dir, 'bot', 'interfaces')
        if os.path.exists(bot_interfaces_path):
            sys.path.insert(0, os.path.join(parent_dir, 'bot'))
            from interfaces import web as bot_web_interface
            BOT_IMPORTS_SUCCESS = True
            print("Successfully imported bot interfaces using direct path insertion")
            return True
    except ImportError as e:
        print(f"Warning: All import approaches failed: {e}")
    
    return False

# Try to import the bot modules
import_bot_modules()

def get_bot_interfaces():
    """Returns the bot web interface if import was successful"""
    return bot_web_interface 