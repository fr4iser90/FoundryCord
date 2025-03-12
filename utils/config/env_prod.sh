#!/usr/bin/env bash

# HomeLab Discord Bot - Production Environment Configuration

# Override defaults for production
export SERVER_HOST="homelab-prod.example.com"
export SERVER_USER="app"
export AUTO_RESTART="false"  # Safer default for production
export REBUILD_ON_DEPLOY="false"
export TEST_TIMEOUT="600"
export WAIT_TIMEOUT="120"

# Production-specific settings
export DEBUG="false"
export VERBOSE_LOGS="false" 