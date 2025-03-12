#!/bin/sh
# Start script for the web application

# Install dependencies if needed
pip install -r requirements.txt

# Set up the app package structure for imports
python setup_app_package.py

# Run module availability check
python main_check.py

# Run the initialization script
python init.py

# Start the web application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 