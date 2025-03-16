#!/bin/bash
# docker/bot/entrypoint.sh
set -e


# Run Python bootstrap
if python -m app.shared.infrastructure.docker.entrypoint bot; then
    echo "Initialization successful"
else
    echo "Initialization failed"
    exit 1
fi

# Start the Discord bot
#echo "Starting Discord bot..."
#exec python -m app.bot.core.main