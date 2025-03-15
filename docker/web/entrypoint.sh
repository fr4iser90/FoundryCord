#!/bin/bash
# docker/web/entrypoint.sh
set -e

echo "===== Homelab Discord Bot Web Interface Initialization ====="

# Run Python bootstrap
if python -m app.shared.infrastructure.docker.entrypoint web; then
    echo "Initialization successful"
else
    echo "Initialization failed"
    exit 1
fi

# Start the web application
echo "Starting Web Interface..."
exec python -m app.web.core.main