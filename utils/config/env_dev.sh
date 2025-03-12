#!/usr/bin/env bash

# HomeLab Discord Bot - Development Environment Configuration

# Override defaults for development
export SERVER_HOST="192.168.178.33"
export SERVER_USER="docker"
export AUTO_RESTART="true"
export REBUILD_ON_DEPLOY="true"
export TEST_TIMEOUT="300"
export WAIT_TIMEOUT="60"

# Development-specific settings
export DEBUG="true"
export VERBOSE_LOGS="true" 