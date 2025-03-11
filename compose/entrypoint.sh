#!/bin/bash
set -e

echo "===== Homelab Discord Bot Initialization ====="

# Check for credentials file from database
CREDS_FILE="/app/bot/database/credentials/db_credentials"
if [ -f "$CREDS_FILE" ]; then
  echo "Loading database credentials from shared volume..."
  source "$CREDS_FILE"
fi

# Check and set required environment variables
check_required_vars() {
  missing_vars=0
  
  echo "Checking required environment variables..."
  
  # Array of required environment variables
  required_vars=("DISCORD_TOKEN" "DISCORD_SERVER" "SUPER_ADMINS")
  
  for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
      echo "ERROR: Required environment variable $var is not set!"
      missing_vars=$((missing_vars + 1))
    else
      # Don't print tokens/sensitive values
      if [[ "$var" == *"TOKEN"* ]] || [[ "$var" == *"KEY"* ]] || [[ "$var" == *"PASSWORD"* ]]; then
        echo "✓ $var: [Set]"
      else
        echo "✓ $var: ${!var}"
      fi
    fi
  done
  
  if [ $missing_vars -gt 0 ]; then
    echo "Please set the required environment variables and restart the container."
    echo "Container will not start with missing required variables."
    exit 1
  fi
  
  echo "All required environment variables are set."
}

# Apply defaults for other optional variables
apply_variables() {
  echo "Checking environment variables..."
  
  # Set defaults for optional variables if not provided
  export ENVIRONMENT=${ENVIRONMENT:-development}
  export DOMAIN=${DOMAIN:-localhost}
  export OFFLINE_MODE=${OFFLINE_MODE:-false}
  export ENABLED_SERVICES=${ENABLED_SERVICES:-Web}
  
  echo "ENVIRONMENT: ${ENVIRONMENT}"
  echo "DOMAIN: ${DOMAIN}"
  echo "OFFLINE_MODE: ${OFFLINE_MODE}"
  echo "ENABLED_SERVICES: ${ENABLED_SERVICES}"
  
  # Legacy variable support - TYPE was renamed to ENABLED_SERVICES
  if [ -n "$TYPE" ] && [ -z "$ENABLED_SERVICES" ]; then
    export ENABLED_SERVICES="$TYPE"
    echo "Using legacy TYPE variable value for ENABLED_SERVICES: $TYPE"
  fi
}

# Show configuration summary
show_configuration_summary() {
  echo "===== Configuration Summary ====="
  echo "Environment: $ENVIRONMENT"
  
  # Use simple negation to handle all non-true values as false
  if [[ "$OFFLINE_MODE" != "true" ]]; then
    echo "Mode: ONLINE MODE (using real domain)"
    echo "Domain: $DOMAIN"
    
    # Warn if domain is localhost but offline mode is false
    if [ "$DOMAIN" = "localhost" ] && [ "$OFFLINE_MODE" = "false" ]; then
      echo "WARNING: Domain set to localhost but OFFLINE_MODE is false. This may cause issues."
      echo "Consider setting OFFLINE_MODE=true or providing a real domain."
    fi
  else
    echo "Mode: OFFLINE MODE (running with minimal internet connectivity)"
    echo "Domain checks: DISABLED"
    echo "Public IP checks: DISABLED"
    echo "Service URLs: Using local ports"
  fi
  
  echo "Enabled services: $ENABLED_SERVICES"
  echo "============================="
}

# Main initialization function
initialize() {
  # Check for required variables
  check_required_vars
  
  # Apply defaults
  apply_variables
  
  # Show configuration summary
  show_configuration_summary
  
  echo "Starting database initialization..."
  # Use the dedicated Python script for database setup
  if ! python -m infrastructure.database.migrations.init_db; then
    echo "ERROR: Database initialization failed"
    exit 1
  fi
  
  echo "Initialization complete."
}

# Run initialization
initialize

# Start the Discord bot
echo "Starting Discord bot..."
exec python -m core.main