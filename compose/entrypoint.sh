#!/bin/bash
set -e

echo "===== Homelab Discord Bot Initialization ====="

# Check for credentials file from database
CREDS_FILE="/app/bot/database/credentials/db_credentials"
if [ -f "$CREDS_FILE" ]; then
  echo "Loading database credentials from shared volume..."
  source "$CREDS_FILE"
fi

# Function to generate random keys
generate_key() {
  key_type=$1
  
  case $key_type in
    "AES_KEY")
      python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
      ;;
    "ENCRYPTION_KEY")
      python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
      ;;
    "JWT_SECRET_KEY")
      python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(24)).decode())"
      ;;
    *)
      python -c "import secrets; print(secrets.token_hex(16))"
      ;;
  esac
}

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

# Auto-generate optional security keys if not provided and persist them
generate_optional_keys() {
  echo "Checking optional security keys..."
  keys_generated=false
  env_file="/app/bot/config/.env.keys"
  
  # Ensure config directory is writable
  if [ ! -w "/app/bot/config" ]; then
    echo "WARNING: Config directory is not writable. Keys will not be persistent."
    env_file="/tmp/.env.keys.temp"
  fi
  
  # Load previously generated keys if they exist
  if [ -f "$env_file" ]; then
    echo "Loading previously generated keys..."
    source "$env_file"
  fi
  
  # Generate AES_KEY if not set
  if [ -z "$AES_KEY" ]; then
    export AES_KEY=$(generate_key "AES_KEY")
    echo "Generated AES_KEY: ${AES_KEY:0:5}..."
    keys_generated=true
  else
    echo "Using existing AES_KEY: ${AES_KEY:0:5}..."
  fi
  
  # Generate ENCRYPTION_KEY if not set
  if [ -z "$ENCRYPTION_KEY" ]; then
    export ENCRYPTION_KEY=$(generate_key "ENCRYPTION_KEY")
    echo "Generated ENCRYPTION_KEY: ${ENCRYPTION_KEY:0:5}..."
    keys_generated=true
  else
    echo "Using existing ENCRYPTION_KEY: ${ENCRYPTION_KEY:0:5}..."
  fi
  
  # Generate JWT_SECRET_KEY if not set
  if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(generate_key "JWT_SECRET_KEY")
    echo "Generated JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:5}..."
    keys_generated=true
  else
    echo "Using existing JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:5}..."
  fi
  
  # Save the generated keys to a file for persistence between restarts
  if [ "$keys_generated" = true ]; then
    echo "# Generated security keys - DO NOT SHARE" > "$env_file"
    echo "AES_KEY=\"$AES_KEY\"" >> "$env_file"
    echo "ENCRYPTION_KEY=\"$ENCRYPTION_KEY\"" >> "$env_file"
    echo "JWT_SECRET_KEY=\"$JWT_SECRET_KEY\"" >> "$env_file"
    chmod 600 "$env_file"
    echo "Security keys have been saved for persistence between container restarts."
  fi
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
  
  # Generate keys if needed and persist them
  generate_optional_keys
  
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