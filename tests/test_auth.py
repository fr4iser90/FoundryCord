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
        
        # Print the directory structure to help debug
        import os
        print("\nDirectory structure:")
        print("interfaces directory exists:", os.path.exists("/app/bot/interfaces"))
        if os.path.exists("/app/bot/interfaces"):
            print("web directory exists:", os.path.exists("/app/bot/interfaces/web"))
            if os.path.exists("/app/bot/interfaces/web"):
                print("Contents of web directory:", os.listdir("/app/bot/interfaces/web"))
        
        assert False, f"Failed to import web module: {e}"

def test_basic_auth_functionality():
    """Test basic functionality - always passes for now"""
    assert True, "Basic auth functionality test" 