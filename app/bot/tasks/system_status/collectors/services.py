import docker
import socket
import asyncio
import aiohttp
import logging
import os
from dotenv import load_dotenv
import json

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

logger = logging.getLogger('homelab_bot')

def get_container_ip(container_name):
    """Ermittelt die IP-Adresse eines Docker Containers mit der Docker API"""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        # Hole die erste verfügbare IP
        networks = container.attrs['NetworkSettings']['Networks']
        for network in networks.values():
            if network.get('IPAddress'):
                return network['IPAddress']
        return None
    except Exception as e:
        logger.debug(f"Fehler beim Ermitteln der Container-IP für {container_name}: {e}")
        return None

async def check_services_status(include_private=False):
    """Überprüft den Status wichtiger Dienste."""
    services = {}
    
    local_services = [
        {"name": "🎮 Minecraft", "port_range": (25565, 25575), "container": "pufferpanel"},
        {"name": "🎮 Palworld", "port_range": (8211, 8221), "container": "palworld-server"},
        {"name": "🎮 Factorio", "port_range": (34197, 34207), "container": "pufferpanel"},
        {"name": "🎮 Satisfactory", "port_range": (7777, 7787), "container": "satisfactory-server"},
        {"name": "🎮 CS2", "port_range": (27015, 27025), "container": "pufferpanel"},
        {"name": "🎮 Valheim", "port_range": (2456, 2466), "container": "pufferpanel"},
    ]
    
    public_services = [
        {"name": "🎮 Pufferpanel", "url": f"https://pufferpanel.{DOMAIN}"},
        {"name": "☁️ Owncloud", "url": f"https://owncloud.{DOMAIN}"},
        {"name": "🔑 Vaultwarden", "url": f"https://bitwarden.{DOMAIN}"},
    ]
    
    private_services = [
        {"name": "📈 HONEYPOT Grafana", "url": f"https://honeypot-grafana.{DOMAIN}"},      # Aufwärts-Graph statt Dashboard
        {"name": "📊 HONEYPOT Prometheus", "url": f"https://honeypot-prometheus.{DOMAIN}"}, # Dashboard-Icon bleibt passend
        {"name": "🐳 Portainer", "url": f"https://portainer.{DOMAIN}"},                     # Docker-Wal statt Sync-Symbol
    ]
    
    # Wähle die zu prüfenden Services basierend auf include_private
    external_services = public_services + (private_services if include_private else [])
    
    try:
        # Die FUNKTIONIERENDE Methode aus docker.py
        client = docker.from_env()
        containers = client.containers.list(all=True)
        container_dict = {container.name: container for container in containers}
        
        for service in local_services:
            try:
                container = container_dict.get(service["container"])
                if not container:
                    services[service["name"]] = "⚠️ Container nicht gefunden"
                    continue
                
                if container.status != "running":
                    services[service["name"]] = "❌ Offline"
                    continue
                    
                # Rest der Port-Checks nur für laufende Container
                port_start, port_end = service["port_range"]
                active_ports = set()  # Set um Duplikate zu vermeiden
                
                # Prüfe die exponierten Ports des Containers
                if container.attrs.get('NetworkSettings', {}).get('Ports'):
                    for container_port, host_bindings in container.attrs['NetworkSettings']['Ports'].items():
                        container_port_num = int(container_port.split('/')[0])
                        logger.debug(f"Checking port {container_port_num} for {service['name']}")
                        logger.debug(f"Port range: {port_start}-{port_end}")
                        
                        if port_start <= container_port_num <= port_end and host_bindings:
                            host_ip = host_bindings[0]['HostIp'] or 'localhost'
                            host_port = int(host_bindings[0]['HostPort'])
                            logger.debug(f"Found mapped port: {container_port_num} -> {host_ip}:{host_port}")
                            
                            # Verbesserte Port-Prüfung
                            try:
                                # Für 0.0.0.0 oder leere IPs, verwende localhost
                                check_ip = '127.0.0.1' if host_ip in ('0.0.0.0', '') else host_ip
                                
                                # Längeres Timeout für bessere Erkennung
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.settimeout(2)  # Erhöhtes Timeout
                                result = sock.connect_ex((check_ip, host_port))
                                sock.close()
                                
                                if result == 0:  # Port ist aktiv!
                                    active_ports.add(host_port)
                                    logger.debug(f"Port {host_port} is actually active on {check_ip}!")
                                else:
                                    # Wenn TCP-Verbindung fehlschlägt, könnte es UDP sein - füge es als möglichen Port hinzu
                                    protocol = container_port.split('/')[1] if '/' in container_port else 'tcp'
                                    if protocol == 'udp':
                                        logger.debug(f"Port {host_port} may be active (UDP) on {check_ip}")
                                        active_ports.add(host_port)  # Füge UDP-Ports auch hinzu
                            except Exception as e:
                                logger.debug(f"Socket check failed for {host_ip}:{host_port} - {str(e)}")

                logger.debug(f"Service {service['name']} has {len(active_ports)} active ports: {sorted(active_ports)}")

                # Zeige nur die WIRKLICH aktiven Ports
                if active_ports:
                    services[service["name"]] = f"✅ Online auf Port(s): {', '.join(map(str, sorted(active_ports)))}"
                else:
                    services[service["name"]] = "❌ Keine aktiven Ports"
                    
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
    
    except Exception as e:
        logger.debug(f"Fehler bei check_services_status: {str(e)}")
        services = {"error": "⚠️ Fehler beim Überprüfen der Dienste"}
    
    return services