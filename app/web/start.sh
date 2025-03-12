#!/bin/sh
# Start script for the web application

echo "===== Starting HomeLab Discord Bot Web Interface ====="

# Install dependencies if needed
echo "Installing required packages..."
pip install -r requirements.txt

# Set up the app package structure for imports
echo "Setting up Python package structure..."
python setup_app_package.py

# Create necessary directories
mkdir -p /app/app/bot /app/app/web

# Run module availability check
echo "Checking module availability..."
python main_check.py

# Add dependencies needed by the bot
echo "Installing bot dependencies..."
pip install nextcord discord.py

# Run the initialization script
echo "Initializing application..."
python init.py

# Start the web application
echo "Starting web server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 