#!/bin/bash

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if database migrations need to be run
echo "Running database migrations..."
alembic upgrade head

# Start the development server
echo "Starting development server..."
uvicorn interfaces.web.server:app --reload --host 0.0.0.0 --port 8000 