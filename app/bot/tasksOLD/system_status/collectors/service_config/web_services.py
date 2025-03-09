"""Configuration for web-based services"""
import os
from dotenv import load_dotenv

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

def get_public_services():
    return [
        {"name": "🎮 Pufferpanel", "url": f"https://pufferpanel.{DOMAIN}"},
        {"name": "☁️ Owncloud", "url": f"https://owncloud.{DOMAIN}"},
        {"name": "🔑 Vaultwarden", "url": f"https://bitwarden.{DOMAIN}"},
    ]

def get_private_services():
    return [
        {"name": "📈 HONEYPOT Grafana", "url": f"https://honeypot-grafana.{DOMAIN}"},      # Aufwärts-Graph statt Dashboard
        {"name": "📊 HONEYPOT Prometheus", "url": f"https://honeypot-prometheus.{DOMAIN}"}, # Dashboard-Icon bleibt passend
        {"name": "🐳 Portainer", "url": f"https://portainer.{DOMAIN}"},                     # Docker-Wal statt Sync-Symbol
    ]