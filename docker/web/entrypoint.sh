#!/bin/bash
set -e

echo "===== HomeLab Discord Bot Web Interface Initialization ====="

# Function to fetch JWT key from database
fetch_jwt_from_database() {
  echo "Attempting to fetch JWT_SECRET_KEY from database..."
  
  # Check if database is accessible
  if ! pg_isready -h $POSTGRES_HOST -U $APP_DB_USER; then
    echo "Database not ready yet, cannot fetch JWT key"
    return 1
  fi
  
  # Extract JWT key from database
  JWT_FROM_DB=$(PGPASSWORD=$APP_DB_PASSWORD psql -h $POSTGRES_HOST -U $APP_DB_USER -d homelab_bot -t -c "SELECT key_value FROM security_keys WHERE key_name = 'jwt_secret_key' LIMIT 1;")
  
  # Trim whitespace
  JWT_FROM_DB=$(echo $JWT_FROM_DB | xargs)
  
  if [ -n "$JWT_FROM_DB" ]; then
    echo "Found JWT_SECRET_KEY in database"
    export JWT_SECRET_KEY=$JWT_FROM_DB
    return 0
  else
    echo "JWT_SECRET_KEY not found in database"
    return 1
  fi
}

# Check and set required environment variables
check_required_vars() {
  missing_vars=0
  
  echo "Checking required environment variables..."
  
  # Array of required environment variables
  required_vars=("DISCORD_BOT_TOKEN" "DISCORD_BOT_ID" "DISCORD_BOT_SECRET" "APP_DB_PASSWORD")
  
  # First check all variables except JWT_SECRET_KEY
  for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
      echo "ERROR: Required environment variable $var is not set!"
      missing_vars=$((missing_vars + 1))
    else
      # Don't print tokens/sensitive values
      if [[ "$var" == *"TOKEN"* ]] || [[ "$var" == *"KEY"* ]] || [[ "$var" == *"PASSWORD"* ]] || [[ "$var" == *"SECRET"* ]]; then
        echo "✓ $var: [Set]"
      else
        echo "✓ $var: ${!var}"
      fi
    fi
  done
  
  # Try to fetch JWT key from database if not in environment
  if [ -z "$JWT_SECRET_KEY" ]; then
    if fetch_jwt_from_database; then
      echo "✓ JWT_SECRET_KEY: [Retrieved from database]"
    else
      # Generate new JWT key if needed
      echo "Generating new JWT_SECRET_KEY..."
      export JWT_SECRET_KEY=$(openssl rand -base64 24)
      echo "✓ JWT_SECRET_KEY: [Generated new key]"
    fi
  else
    echo "✓ JWT_SECRET_KEY: [Set from environment]"
  fi
  
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
  export DEBUG=${DEBUG:-true}
  export REDIS_HOST=${REDIS_HOST:-redis}
  export REDIS_PORT=${REDIS_PORT:-6379}
  export DISCORD_REDIRECT_URI=${DISCORD_REDIRECT_URI:-http://localhost:8000/auth/callback}
  export APP_DB_USER=${APP_DB_USER:-homelab_discord_bot}
  export POSTGRES_HOST=${POSTGRES_HOST:-postgres}
  
  echo "ENVIRONMENT: ${ENVIRONMENT}"
  echo "DEBUG: ${DEBUG}"
  echo "REDIS_HOST: ${REDIS_HOST}"
  echo "REDIS_PORT: ${REDIS_PORT}"
  echo "DISCORD_REDIRECT_URI: ${DISCORD_REDIRECT_URI}"
  echo "APP_DB_USER: ${APP_DB_USER}"
  echo "POSTGRES_HOST: ${POSTGRES_HOST}"
}

# Show configuration summary
show_configuration_summary() {
  echo "===== Configuration Summary ====="
  echo "Environment: $ENVIRONMENT"
  echo "Debug Mode: $DEBUG"
  echo "Redis: $REDIS_HOST:$REDIS_PORT"
  echo "Database Host: $POSTGRES_HOST"
  echo "Discord Redirect URI: $DISCORD_REDIRECT_URI"
  echo "============================="
}

# Wait for database to be ready
wait_for_database() {
  echo "Waiting for database to be ready..."
  
  # Check if postgres host is available
  max_retries=30
  retry_interval=2
  retries=0
  
  while [ $retries -lt $max_retries ]; do
    if pg_isready -h $POSTGRES_HOST -U $APP_DB_USER; then
      echo "Database is ready!"
      return 0
    fi
    
    retries=$((retries + 1))
    echo "Database not ready yet. Retry $retries/$max_retries..."
    sleep $retry_interval
  done
  
  echo "ERROR: Failed to connect to database after $max_retries attempts."
  exit 1
}

# Main initialization function
initialize() {
  # Check for required variables
  check_required_vars
  
  # Apply defaults
  apply_variables
  
  # Show configuration summary
  show_configuration_summary
  
  # Wait for database
  # wait_for_database
  
  # Install dependencies if needed
  echo "Installing required packages..."
  pip install -r requirements.txt
  
  echo "Initialization complete."
}

# Run initialization
initialize

# Start the web application
echo "Starting Web Interface..."
exec python -m app.web.core.main

