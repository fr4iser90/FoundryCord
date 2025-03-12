"""
Initialization script for the web application.
"""
import os

def check_env_file():
    """Ensure .env file exists with required variables"""
    env_file = "app/web/.env"
    if not os.path.exists(env_file):
        print(f"Warning: {env_file} does not exist. Creating template file.")
        with open(env_file, "w") as f:
            f.write("""# Discord OAuth Configuration
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key

# Database Configuration
DATABASE_URL=sqlite:///./homelab_bot.db
""")

def main():
    """Main initialization function"""
    print("=== Web Application Initialization ===")
    
    # Check environment file
    check_env_file()
    
    print("Initialization complete.")

if __name__ == "__main__":
    main() 