#!/bin/sh
# Start script for the web application

# Run the initialization script
python init.py

# Start the web application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 