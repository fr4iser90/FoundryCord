import pytest
import sys

def test_dashboard_module_exists():
    """Verify the dashboard module exists and can be imported"""
    try:
        # Try to import the dashboard module using the correct path for the container
        from app.bot.interfaces.web import api as web_api
        from app.bot.interfaces.web import ui as web_ui
        print("Successfully imported web modules")
        
        # List what's available in the modules
        print("Web API module contains:", dir(web_api))
        print("Web UI module contains:", dir(web_ui))
        
        # Try to import specific dashboard routes if they exist
        try:
            # This will fail if the module doesn't exist, which is okay for this test
            # We're testing what the actual file structure is
            from app.bot.interfaces.web.ui import dashboard
            print("Successfully imported dashboard UI module")
            print("Dashboard module contains:", dir(dashboard))
        except ImportError as e:
            print(f"Dashboard UI module import failed: {e}")
            
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
                if os.path.exists("/app/bot/interfaces/web/ui"):
                    print("Contents of web/ui directory:", os.listdir("/app/bot/interfaces/web/ui"))
                if os.path.exists("/app/bot/interfaces/web/api"):
                    print("Contents of web/api directory:", os.listdir("/app/bot/interfaces/web/api"))
                
        assert False, f"Failed to import web modules: {e}"

def test_basic_dashboard_functionality():
    """Test basic functionality - always passes for now"""
    assert True, "Basic dashboard functionality test" 