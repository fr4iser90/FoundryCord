"""
Initialization script for the web application.
Handles database migrations and startup tasks.
"""
import os
import subprocess
import sys
from pathlib import Path

def run_migrations():
    """Run database migrations using Alembic"""
    print("Running database migrations...")
    try:
        # Change to the directory containing alembic.ini if necessary
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("=== Web Application Initialization ===")
    
    # Ensure the application directory is in the Python path
    app_dir = Path(__file__).parent.parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    # Run database migrations if requested
    if os.environ.get("RUN_MIGRATIONS", "false").lower() == "true":
        success = run_migrations()
        if not success:
            print("Failed to run migrations. Exiting.")
            sys.exit(1)
    
    print("Initialization complete. Starting web application...")

if __name__ == "__main__":
    main() 