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
        result = subprocess.check_call([sys.executable, "-m", "pip", "install", "nextcord", "discord.py"])
        print("Dependencies installed successfully")
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
    
    # Try multiple import approaches in sequence
    import_attempts = [
        # Approach 1: Using absolute imports with app.bot
        lambda: __import__('app.bot.interfaces.web', fromlist=['*']),
        
        # Approach 2: Using relative imports with bot
        lambda: __import__('bot.interfaces.web', fromlist=['*']),
        
        # Approach 3: Dynamic import with importlib
        lambda: importlib.import_module('app.bot.interfaces.web'),
        
        # Approach 4: Direct path manipulation
        lambda: import_with_path_manipulation(),
        
        # Approach 5: Create a simplified mock interface if all else fails
        lambda: create_mock_interface()
    ]
    
    for i, import_attempt in enumerate(import_attempts):
        try:
            print(f"Trying import approach {i+1}...")
            bot_web_interface = import_attempt()
            BOT_IMPORTS_SUCCESS = True
            print(f"Successfully imported bot interfaces using approach {i+1}")
            return True
        except ImportError as e:
            print(f"Import approach {i+1} failed: {e}")
        except Exception as e:
            print(f"Unexpected error with import approach {i+1}: {e}")
    
    print("WARNING: All import approaches failed. Using fallback empty interface")
    return False

def import_with_path_manipulation():
    """Import using direct path manipulation"""
    bot_interfaces_path = os.path.join(parent_dir, 'bot', 'interfaces')
    if os.path.exists(bot_interfaces_path):
        sys.path.insert(0, os.path.join(parent_dir, 'bot'))
        from interfaces import web as imported_web
        return imported_web
    raise ImportError(f"Path {bot_interfaces_path} does not exist")

def create_mock_interface():
    """Create a minimal mock interface when imports fail"""
    class MockInterface:
        """Mock interface when real bot interface is unavailable"""
        def __init__(self):
            self.name = "Mock Bot Interface"
            
        def get_status(self):
            return {"status": "offline", "message": "Bot interface unavailable"}
    
    print("WARNING: Creating mock interface as fallback")
    return MockInterface()

# Try to import the bot modules
import_result = import_bot_modules()

def get_bot_interfaces():
    """Returns the bot web interface if import was successful"""
    return bot_web_interface 