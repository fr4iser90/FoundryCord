#!/bin/bash
set -e

echo "===== Homelab Discord Bot Initialization ====="

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
  required_vars=("DISCORD_TOKEN" "DISCORD_SERVER" "HOMELAB_CATEGORY_ID" "SUPER_ADMINS")
  
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
  
  # Create config directory if it doesn't exist
  mkdir -p /app/bot/config
  
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
  
  # Database password checks
  if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "WARNING: POSTGRES_PASSWORD not set, using default from compose file."
  fi
  
  if [ -z "$APP_DB_PASSWORD" ]; then
    echo "WARNING: APP_DB_PASSWORD not set, using default from compose file."
  fi
}

# Apply defaults for other optional variables
apply_defaults() {
  echo "Applying defaults for optional variables..."
  
  # Define defaults
  declare -A defaults
  defaults["ENVIRONMENT"]="development"
  defaults["DOMAIN"]="localhost"
  defaults["TYPE"]="Web,Game,File"
  defaults["SESSION_DURATION_HOURS"]="24"
  defaults["RATE_LIMIT_WINDOW"]="60"
  defaults["RATE_LIMIT_MAX_ATTEMPTS"]="5"
  defaults["PUID"]="1001"
  defaults["PGID"]="987"
  
  # Apply defaults if not set
  for key in "${!defaults[@]}"; do
    if [ -z "${!key}" ]; then
      export "$key"="${defaults[$key]}"
      echo "Set default for $key: ${defaults[$key]}"
    fi
  done
}

# Main initialization function
initialize() {
  # Check for required variables
  check_required_vars
  
  # Generate keys if needed and persist them
  generate_optional_keys
  
  # Apply defaults
  apply_defaults
  
  # Wait for PostgreSQL if needed
  if [ "$WAIT_FOR_DB" = "true" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    python -m infrastructure.database.migrations.wait_for_postgres
  fi
  
  # Create database tables - skip if DB_INIT_DISABLE is set
  if [ "$DB_INIT_DISABLE" != "true" ]; then
    echo "Initializing database..."
    python -m infrastructure.database.migrations.init_db
  fi
  
  echo "Initialization complete."
}

# Run initialization
initialize

# Start the Discord bot
echo "Starting Discord bot..."
exec python -m core.main