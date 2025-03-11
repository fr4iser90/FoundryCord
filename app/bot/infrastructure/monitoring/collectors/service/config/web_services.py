"""Configuration for web-based services"""
import os
from dotenv import load_dotenv
from infrastructure.config.feature_flags import get_service_url

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

def get_public_services():
    return [
        {"name": "⚙️ Pufferpanel", "url": get_service_url("pufferpanel", use_https=True)},
        {"name": "☁️ Owncloud", "url": get_service_url("owncloud", use_https=True)},
        {"name": "🔑 Vaultwarden", "url": get_service_url("bitwarden", use_https=True)},
    ]

def get_private_services():
    return [
        {"name": "📈 HONEYPOT Grafana", "url": get_service_url("honeypot-grafana", use_https=True)},
        {"name": "📊 HONEYPOT Prometheus", "url": get_service_url("honeypot-prometheus", use_https=True)},
        {"name": "🐳 Portainer", "url": get_service_url("portainer", use_https=True)},
    ]