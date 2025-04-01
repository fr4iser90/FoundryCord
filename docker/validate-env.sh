#!/bin/bash

# Environment variable validation script
ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"
REQUIRED_VARS=()
MISSING_VARS=0

# Function to extract required variables from .env.example
extract_required_vars() {
  while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    # Check for lines with (REQUIRED) in the comment
    if [[ "$line" =~ .*#.*\(REQUIRED\).* ]]; then
      # Extract the variable name (part before =)
      var_name=$(echo "$line" | cut -d '=' -f 1)
      REQUIRED_VARS+=("$var_name")
    fi
  done < "$ENV_EXAMPLE_FILE"
}

# Function to check if required variables exist and have values
check_required_vars() {
  for var in "${REQUIRED_VARS[@]}"; do
    # Get value from .env file
    value=$(grep "^$var=" "$ENV_FILE" | cut -d '=' -f 2-)
    
    # Check if variable exists and has a non-empty value
    if [[ -z "$value" || "$value" == " " ]]; then
      echo "ERROR: Required variable '$var' is missing or empty in $ENV_FILE"
      MISSING_VARS=$((MISSING_VARS+1))
    fi
  done
}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE file not found. Please copy $ENV_EXAMPLE_FILE to $ENV_FILE and fill in required values."
  exit 1
fi

# Extract and check required variables
extract_required_vars
check_required_vars

# If any required variables are missing, exit with error
if [ $MISSING_VARS -gt 0 ]; then
  echo "ERROR: $MISSING_VARS required variable(s) missing. Please update your $ENV_FILE file."
  exit 1
else
  echo "Environment validation successful! All required variables are set."
  exit 0
fi
