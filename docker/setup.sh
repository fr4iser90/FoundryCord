#!/bin/bash

# Setup script for FoundryCord
# Determine the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE_FILE="${SCRIPT_DIR}/.env.example"

echo "Script running from: ${SCRIPT_DIR}"
echo "Using example file: ${ENV_EXAMPLE_FILE}"
echo "Target env file: ${ENV_FILE}"

# Check if .env file exists
if [ -f "$ENV_FILE" ]; then
  read -p "An existing $ENV_FILE file was found. Overwrite? (y/n): " overwrite
  if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
    echo "Setup canceled. Using existing $ENV_FILE file."
    exit 0
  fi
fi

# Check if .env.example exists
if [ ! -f "$ENV_EXAMPLE_FILE" ]; then
  echo "ERROR: Example file $ENV_EXAMPLE_FILE not found!"
  exit 1
fi

# Copy example file
cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
echo "Created $ENV_FILE from template."

# Function to update a variable in the .env file
update_var() {
  local var_name="$1"
  local prompt="$2"
  local default="$3"
  
  # Get the current value if it exists
  current_val=$(grep "^$var_name=" "$ENV_FILE" | cut -d '=' -f 2-)
  
  # Use default if provided and no current value
  if [[ -z "$current_val" && -n "$default" ]]; then
    current_val="$default"
  fi
  
  # Show current value in prompt if it exists
  if [[ -n "$current_val" ]]; then
    read -p "$prompt [$current_val]: " new_val
  else
    read -p "$prompt: " new_val
  fi
  
  # Use current value if new value is empty
  if [[ -z "$new_val" && -n "$current_val" ]]; then
    new_val="$current_val"
  # Use default if new value and current value are empty
  elif [[ -z "$new_val" && -z "$current_val" && -n "$default" ]]; then
    new_val="$default"
  fi
  
  # Update the variable in the .env file
  if [[ -n "$new_val" ]]; then
    # Use sed differently based on OS (macOS vs Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|^$var_name=.*|$var_name=$new_val|" "$ENV_FILE"
    else
      sed -i "s|^$var_name=.*|$var_name=$new_val|" "$ENV_FILE"
    fi
    echo "Updated $var_name."
  fi
}

echo "Please provide values for required configuration:"
update_var "DISCORD_BOT_TOKEN" "Discord Bot Token"
update_var "OWNER" "Owner username and ID (format: USERNAME|ID)"
update_var "ENVIRONMENT" "Environment (development, production, testing)" "development"
update_var "DOMAIN" "Domain or IP address"
update_var "ENABLED_SERVICES" "Enabled services (comma-separated list)" "Web,Game,File"

echo "Database configuration:"
update_var "POSTGRES_HOST" "PostgreSQL host" "foundrycord-db"
update_var "POSTGRES_PORT" "PostgreSQL port" "5432"
update_var "POSTGRES_DB" "PostgreSQL database name" "foundrycord"
update_var "POSTGRES_USER" "PostgreSQL admin username" "postgres"
update_var "APP_DB_USER" "Application database username" "foundrycord_bot"
update_var "POSTGRES_PASSWORD" "PostgreSQL admin password" "postgres_dev_password"
update_var "APP_DB_PASSWORD" "Application database password" "app_dev_password"

echo "Setup complete! You can now run 'docker-compose up -d' to start the services."