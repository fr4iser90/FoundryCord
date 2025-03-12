#!/bin/sh
# Start script for the web application

echo "===== Starting HomeLab Discord Bot Web Interface ====="

# Install dependencies if needed
echo "Installing required packages..."
pip install -r requirements.txt

# Create necessary directories for package structure
echo "Setting up directory structure..."
mkdir -p /app/app/web /app/app/bot

# Set up the app package structure for imports
echo "Setting up Python package structure..."
python setup_app_package.py

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
cd /app/web  # Ensure we're in the correct directory
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 