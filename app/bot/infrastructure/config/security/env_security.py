#!/usr/bin/env python3
# app/bot/infrastructure/config/security/env_security.py

import os
import sys
import getpass
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from infrastructure.logging import logger

# Required environment variables with descriptions
REQUIRED_VARS = {
    # Discord Bot Variables
    "DISCORD_TOKEN": "Your Discord bot token from the Discord Developer Portal",
    "ENVIRONMENT": "Environment type (development, production)",
    "DOMAIN": "Your domain name (e.g., example.com)",
    "DISCORD_SERVER": "Your Discord server/guild ID",
    "HOMELAB_CATEGORY_ID": "Discord category ID for Homelab channels",
    
    # Database Variables
    "POSTGRES_HOST": "PostgreSQL host (e.g., homelab-postgres)",
    "POSTGRES_PORT": "PostgreSQL port (default: 5432)",
    "POSTGRES_USER": "PostgreSQL admin username",
    "POSTGRES_PASSWORD": "PostgreSQL admin password",
    "POSTGRES_DB": "PostgreSQL database name",
    "APP_DB_USER": "Application database user",
    "APP_DB_PASSWORD": "Application database password",
}

# Variables that should be auto-generated for security
AUTO_GENERATE = {
    "AES_KEY": lambda: base64.urlsafe_b64encode(os.urandom(32)).decode(),
    "ENCRYPTION_KEY": lambda: Fernet.generate_key().decode(),
    "JWT_SECRET_KEY": lambda: base64.urlsafe_b64encode(os.urandom(24)).decode(),
}

def generate_encryption_key(master_password):
    """Generate a Fernet key from master password"""
    salt = b'homelab_bot_salt'  # In production, this should be stored securely
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def encrypt_data(data, key):
    """Encrypt data using Fernet"""
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(encrypted_data, key):
    """Decrypt data using Fernet"""
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return json.loads(decrypted)
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

def get_env_value(var_name, description, current_value=None):
    """Get environment variable value from user input"""
    if current_value:
        default_display = f" [{current_value}]" 
    else:
        default_display = ""
        
    if "PASSWORD" in var_name or "TOKEN" in var_name or "SECRET" in var_name:
        value = getpass.getpass(f"{description}{default_display}: ")
    else:
        value = input(f"{description}{default_display}: ")
        
    # Use default if user presses enter
    if not value and current_value:
        return current_value
    return value

def load_current_env():
    """Load current environment variables from .env files"""
    env_vars = {}
    
    # Try to load from .env.discordbot
    try:
        with open("compose/.env.discordbot", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
        
    # Try to load from .env.postgres
    try:
        with open("compose/.env.postgres", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
        
    return env_vars

def main():
    print("===== Homelab Discord Bot Setup =====")
    print("This script will help you set up the required environment variables.")
    
    # Load current environment values if they exist
    current_env = load_current_env()
    
    # Check for environment mode
    if "ENVIRONMENT" in current_env:
        env_mode = current_env["ENVIRONMENT"]
    else:
        env_mode = input("Select environment (development/production) [development]: ").lower() or "development"
        current_env["ENVIRONMENT"] = env_mode
    
    # Ask for master password for encryption
    master_password = getpass.getpass("Enter a master password to encrypt sensitive data: ")
    if not master_password:
        print("Error: Master password is required")
        sys.exit(1)
    
    encryption_key = generate_encryption_key(master_password)
    
    # Collect all required variables
    env_vars = {}
    for var_name, description in REQUIRED_VARS.items():
        current = current_env.get(var_name, os.getenv(var_name, ""))
        env_vars[var_name] = get_env_value(var_name, description, current)
    
    # Auto-generate security keys if they don't exist
    for var_name, generator in AUTO_GENERATE.items():
        if var_name not in current_env or not current_env[var_name]:
            env_vars[var_name] = generator()
            print(f"Auto-generated {var_name}")
        else:
            env_vars[var_name] = current_env[var_name]
    
    # Add other default values
    env_vars.update({
        "TYPE": "Web,Game,File",
        "SESSION_DURATION_HOURS": "24",
        "RATE_LIMIT_WINDOW": "60",
        "RATE_LIMIT_MAX_ATTEMPTS": "5",
        "PUID": "1001",
        "PGID": "987"
    })
    
    # Encrypt and save the variables
    encrypted_data = encrypt_data(env_vars, encryption_key)
    with open("../../.env.encrypted", "w") as f:
        f.write(encrypted_data)
    
    # Create startup scripts
    with open("load_env.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import json
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key(password):
    salt = b'homelab_bot_salt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def decrypt_data(encrypted_data, key):
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return json.loads(decrypted)
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

def main():
    # Read the encrypted data
    try:
        with open("../../.env.encrypted", "r") as f:
            encrypted_data = f.read()
    except FileNotFoundError:
        print("Error: .env.encrypted file not found. Run setup.py first.")
        sys.exit(1)
    
    # Get the master password
    password = getpass.getpass("Enter master password to decrypt environment variables: ")
    key = generate_key(password)
    
    # Decrypt and set environment variables
    env_vars = decrypt_data(encrypted_data, key)
    if not env_vars:
        print("Error: Failed to decrypt environment variables.")
        sys.exit(1)
    
    # Export variables to environment
    for var_name, value in env_vars.items():
        os.environ[var_name] = value
    
    print("Environment variables loaded successfully.")
    
    # If arguments provided, execute them
    if len(sys.argv) > 1:
        import subprocess
        subprocess.run(sys.argv[1:])

if __name__ == "__main__":
    main()
""")
    
    # Create a .env generator for Docker compatibility
    with open("generate_env_files.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import json
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key(password):
    salt = b'homelab_bot_salt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def decrypt_data(encrypted_data, key):
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return json.loads(decrypted)
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

def main():
    # Read the encrypted data
    try:
        with open("../../.env.encrypted", "r") as f:
            encrypted_data = f.read()
    except FileNotFoundError:
        print("Error: .env.encrypted file not found. Run setup.py first.")
        sys.exit(1)
    
    # Get the master password
    password = getpass.getpass("Enter master password to decrypt environment variables: ")
    key = generate_key(password)
    
    # Decrypt environment variables
    env_vars = decrypt_data(encrypted_data, key)
    if not env_vars:
        print("Error: Failed to decrypt environment variables.")
        sys.exit(1)
    
    # Create .env.discordbot
    discord_vars = [
        "DISCORD_TOKEN", "ENVIRONMENT", "DOMAIN", "AES_KEY", "TYPE",
        "AUTH_TOKEN", "TRACKER_URL", "HOMELAB_CATEGORY_ID", 
        "HOMELAB_GAMESERVER_CATEGORY_ID", "DISCORD_SERVER", 
        "SUPER_ADMINS", "ADMINS", "USERS", "ENCRYPTION_KEY",
        "JWT_SECRET_KEY", "SESSION_DURATION_HOURS", "RATE_LIMIT_WINDOW",
        "RATE_LIMIT_MAX_ATTEMPTS", "PUID", "PGID"
    ]
    
    with open("compose/.env.discordbot", "w") as f:
        for var in discord_vars:
            if var in env_vars:
                f.write(f"{var}={env_vars[var]}\\n")
    
    # Create .env.postgres
    postgres_vars = [
        "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", 
        "POSTGRES_PASSWORD", "POSTGRES_DB", "APP_DB_USER", "APP_DB_PASSWORD"
    ]
    
    with open("compose/.env.postgres", "w") as f:
        for var in postgres_vars:
            if var in env_vars:
                f.write(f"{var}={env_vars[var]}\\n")
    
    print("Environment files generated successfully.")
    print("compose/.env.discordbot and compose/.env.postgres have been created.")
    print("NOTE: These files contain sensitive information in plaintext for Docker compatibility.")
    print("      Consider restricting their permissions with 'chmod 600 compose/.env.*'")

if __name__ == "__main__":
    main()
""")
    
    # Make scripts executable
    os.chmod("load_env.py", 0o755)
    os.chmod("generate_env_files.py", 0o755)
    
    print("\n===== Setup Complete =====")
    print("Your environment variables have been encrypted and saved to .env.encrypted")
    print("To load these variables:")
    print("  1. For local development: ./load_env.py python app/bot/core/main.py")
    print("  2. For Docker: ./generate_env_files.py (creates .env files)")
    print("\nIMPORTANT: Remember your master password! It's required to decrypt your environment variables.")

if __name__ == "__main__":
    main()