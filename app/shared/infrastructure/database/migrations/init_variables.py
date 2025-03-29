#!/usr/bin/env python3
# setup.py

import os
import sys
import secrets
import base64
import getpass
import subprocess
from cryptography.fernet import Fernet
import argparse
from pathlib import Path

# Parse command line arguments
parser = argparse.ArgumentParser(description="Setup Homelab Discord Bot environment")
parser.add_argument("--minimal", action="store_true", help="Request only essential variables")
parser.add_argument("--advanced", action="store_true", help="Request all configuration options")
parser.add_argument("--auto", action="store_true", help="Use auto-generated values where possible")
args = parser.parse_args()

# Define the minimal required variables that MUST be provided by the user
ESSENTIAL_VARS = {
    "DISCORD_BOT_TOKEN": "Your Discord bot token from Discord Developer Portal",
    "DISCORD_SERVER": "Your Discord server/guild ID",
    #"HOMELAB_CATEGORY_ID": "Category ID for Homelab channels",
    "OWNER": "Discord user IDs for super admins (format: NAME|ID)",
}

# Variables that can be auto-generated
AUTO_GENERATE = {
    "AES_KEY": lambda: base64.urlsafe_b64encode(os.urandom(32)).decode(),
    "ENCRYPTION_KEY": lambda: Fernet.generate_key().decode(),
    "JWT_SECRET_KEY": lambda: base64.urlsafe_b64encode(os.urandom(24)).decode(),
    "POSTGRES_PASSWORD": lambda: secrets.token_hex(16),
    "APP_DB_PASSWORD": lambda: secrets.token_hex(16),
    "HOMELAB_CATEGORY_ID": lambda: "auto",  # Will be created during bot startup
    "GAMESERVERS_CATEGORY_ID": lambda: "auto",  # Will be created during bot startup
}

# Default values for optional variables
DEFAULT_VALUES = {
    "ENVIRONMENT": "development",
    "DOMAIN": "localhost",
    "TYPE": "Web,Game,File",
    "POSTGRES_HOST": "discord-server-db",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_DB": "homelab",
    "APP_DB_USER": "homelab_discord_bot",
    "SESSION_DURATION_HOURS": "24",
    "RATE_LIMIT_WINDOW": "60",
    "RATE_LIMIT_MAX_ATTEMPTS": "5",
    "PUID": "1001",
    "PGID": "987",
}

def get_input(prompt, default=None, sensitive=False):
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if sensitive:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def generate_env_files(config):
    """Generate .env.discordbot and .env.postgres files"""
    # Create compose directory if it doesn't exist
    Path("compose").mkdir(exist_ok=True)
    
    # Variables for .env.discordbot
    discord_vars = [
        "DISCORD_BOT_TOKEN", "ENVIRONMENT", "DOMAIN", "AES_KEY", "TYPE",
        "AUTH_TOKEN", "TRACKER_URL", "HOMELAB_CATEGORY_ID", 
        "HOMELAB_GAMESERVER_CATEGORY_ID", "DISCORD_SERVER", 
        "OWNER", "ADMINS", "USERS", "ENCRYPTION_KEY",
        "JWT_SECRET_KEY", "SESSION_DURATION_HOURS", "RATE_LIMIT_WINDOW",
        "RATE_LIMIT_MAX_ATTEMPTS", "PUID", "PGID"
    ]
    
    #with open("compose/.env.discordbot", "w") as f:
    with open("compose/.env", "w") as f:
        for var in discord_vars:
            if var in config:
                f.write(f"{var}={config[var]}\n")
    
    # Variables for .env.postgres
    postgres_vars = [
        "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", 
        "POSTGRES_PASSWORD", "POSTGRES_DB", "APP_DB_USER", "APP_DB_PASSWORD"
    ]
    
    #with open("compose/.env.postgres", "w") as f:
    with open("compose/.env", "w") as f:
        for var in postgres_vars:
            if var in config:
                f.write(f"{var}={config[var]}\n")
    
    print("Environment files generated successfully!")
    print("compose/.env.discordbot and compose/.env.postgres have been created.")
    
    # Set appropriate permissions
    os.chmod("compose/.env", 0o600)
    #os.chmod("compose/.env.postgres", 0o600)
    print("File permissions set to 600 (user read/write only)")

def main():
    print("===== Homelab Discord Bot Setup =====")
    
    # Load existing values if available
    config = {}
    try:
        #with open("compose/.env.discordbot", "r") as f:
        with open("compose/.env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    except FileNotFoundError:
        pass
    
    try:
        with open("compose/.env.postgres", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    except FileNotFoundError:
        pass
    
    # Auto-generate values if requested
    if args.auto:
        for key, generator in AUTO_GENERATE.items():
            if key not in config or not config[key]:
                config[key] = generator()
                print(f"Auto-generated {key}")
    
    # Set default values for unspecified optional variables
    for key, value in DEFAULT_VALUES.items():
        if key not in config or not config[key]:
            config[key] = value
    
    # Always ask for essential variables
    for key, description in ESSENTIAL_VARS.items():
        is_sensitive = "TOKEN" in key or "PASSWORD" in key or "SECRET" in key
        current = config.get(key, "")
        
        # Don't show tokens in the prompt
        display_current = "[set]" if current and is_sensitive else current
        
        value = get_input(f"{description}", default=display_current, sensitive=is_sensitive)
        if value:
            config[key] = value
    
    # Ask for additional variables if in advanced mode
    if args.advanced:
        for key, value in DEFAULT_VALUES.items():
            is_sensitive = "TOKEN" in key or "PASSWORD" in key or "SECRET" in key
            current = config.get(key, value)
            
            # Don't show tokens in the prompt
            display_current = "[set]" if current and is_sensitive else current
            
            new_value = get_input(f"{key}", default=display_current, sensitive=is_sensitive)
            if new_value:
                config[key] = new_value
                
        # Ask for auto-generated values too if in advanced mode
        for key, generator in AUTO_GENERATE.items():
            if key not in ESSENTIAL_VARS:  # Skip if already asked
                is_sensitive = "TOKEN" in key or "PASSWORD" in key or "SECRET" in key
                current = config.get(key, "")
                
                # Don't show tokens in the prompt
                display_current = "[set]" if current and is_sensitive else "[auto-generate]"
                
                new_value = get_input(f"{key}", default=display_current, sensitive=is_sensitive)
                if new_value == "[auto-generate]":
                    config[key] = generator()
                elif new_value:
                    config[key] = new_value
    
    # Generate the environment files
    generate_env_files(config)
    
    # Ask if user wants to start the containers
    if input("Do you want to start the containers now? (y/n): ").lower() == 'y':
        try:
            subprocess.run(["docker", "compose", "-f", "compose/docker-compose.yml", "up", "-d"], check=True)
            print("Containers started successfully!")
        except subprocess.CalledProcessError:
            print("Failed to start containers. Please check the error and try again manually.")

if __name__ == "__main__":
    main()