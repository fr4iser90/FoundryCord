import os
from dotenv import load_dotenv

load_dotenv()

# Core environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()
DOMAIN = os.getenv('DOMAIN', 'localhost')
OFFLINE_MODE = os.getenv('OFFLINE_MODE', 'true').lower() == 'true'

# Derived feature flags
ENABLE_DOMAIN_CHECKS = not OFFLINE_MODE and DOMAIN != 'localhost'
ENABLE_PUBLIC_IP_CHECKS = not OFFLINE_MODE
ENABLE_EXTERNAL_WEB_CHECKS = not OFFLINE_MODE

# Conditional settings
LOCAL_PORTS = {
    "pufferpanel": 8080,
    "owncloud": 8081,
    "bitwarden": 8082,
    "honeypot-grafana": 3000,
    "honeypot-prometheus": 9090,
    "portainer": 9000,
    # Add other services as needed
}

def get_service_url(service_name, use_https=False):
    """Get the appropriate URL for a service based on mode"""
    if OFFLINE_MODE or DOMAIN == 'localhost':
        port = LOCAL_PORTS.get(service_name, 80)
        return f"http://localhost:{port}"
    else:
        protocol = "https" if use_https else "http"
        return f"{protocol}://{service_name}.{DOMAIN}"