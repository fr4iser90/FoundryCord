import socket
import asyncio
import aiohttp
import subprocess
import logging
import os
from dotenv import load_dotenv

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

logger = logging.getLogger('homelab_bot')

async def check_services_status():
    """Überprüft den Status wichtiger Dienste."""
    services = {}
    
    local_services = [
        {"name": "🔐 SSH", "port": 22},
    ]
    
    external_services = [
        {"name": "☁️ Owncloud", "url": f"https://owncloud.{DOMAIN}"},
        {"name": "💾 Pufferfish", "url": f"https://pufferpanel.{DOMAIN}"},
        {"name": "💾 Vaultwarden", "url": f"https://bw.{DOMAIN}"},
        {"name": "📊 Grafana", "url": f"https://grafana.{DOMAIN}"},
        {"name": "📝 Nextcloud", "url": f"https://nextcloud.{DOMAIN}"},
        {"name": "🔄 Portainer", "url": f"https://portainer.{DOMAIN}"},
    ]
    
    auth_required_services = [
        "🔄 Portainer",
        "📊 Grafana",
        "💾 Vaultwarden",
    ]

    for service in local_services:
        try:
            if service["port"] == 22:
                ssh_running = False
                try:
                    result = subprocess.run(["pgrep", "sshd"], capture_output=True, text=True)
                    ssh_running = result.returncode == 0
                except:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    ssh_running = sock.connect_ex(('127.0.0.1', 22)) == 0
                    sock.close()
                
                services[service["name"]] = "✅ Online" if ssh_running else "❌ Offline"
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', service["port"]))
                if result == 0:
                    services[service["name"]] = "✅ Online"
                else:
                    services[service["name"]] = "❌ Offline"
                sock.close()
        except Exception as e:
            logger.debug(f"Fehler bei {service['name']}: {str(e)}")
            services[service["name"]] = "⚠️ Fehler"
    
    async with aiohttp.ClientSession() as session:
        for service in external_services:
            try:
                async with session.get(service["url"], timeout=5, ssl=False) as response:
                    if response.status < 400:
                        services[service["name"]] = "✅ Online"
                    elif response.status in [401, 403]:
                        services[service["name"]] = "🔒 Geschützt"
                    else:
                        services[service["name"]] = f"❌ Status {response.status}"
            except asyncio.TimeoutError:
                services[service["name"]] = "⏱️ Timeout"
            except Exception as e:
                logger.debug(f"Fehler bei {service['name']}: {str(e)}")
                services[service["name"]] = "❌ Offline"
    
    return services