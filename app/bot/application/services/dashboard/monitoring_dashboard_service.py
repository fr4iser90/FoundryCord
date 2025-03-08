import psutil
import socket
import os
import asyncio
from datetime import datetime
import requests
from infrastructure.logging import logger
from utils.http_client import http_client

class MonitoringDashboardService:
    def __init__(self, bot):
        self.bot = bot
        self.domain = os.getenv('DOMAIN', 'Nicht konfiguriert')

    async def get_system_status(self):
        """Holt die Systemdaten für das Dashboard"""
        try:
            # CPU, Memory, Disk usage
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Netzwerkstatus prüfen
            network_status = {
                'up': True,
                'latency': 0
            }
            
            try:
                # Ping-Test (vereinfacht)
                start_time = datetime.now()
                requests.get('https://google.com', timeout=2)
                end_time = datetime.now()
                network_status['latency'] = (end_time - start_time).total_seconds() * 1000
            except:
                network_status['up'] = False
                network_status['latency'] = 999
            
            # Public IP
            try:
                public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
            except:
                public_ip = "Nicht verfügbar"
            
            # Domain-IP prüfen
            try:
                domain_ip = socket.gethostbyname(self.domain)
                ip_match = public_ip == domain_ip
            except:
                domain_ip = "Nicht auflösbar"
                ip_match = False
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': {
                    'percent': memory.percent,
                    'used': memory.used / (1024**3),  # GB
                    'total': memory.total / (1024**3)  # GB
                },
                'disk_usage': {
                    'percent': disk.percent,
                    'used': disk.used / (1024**3),  # GB
                    'total': disk.total / (1024**4)  # TB
                },
                'network_status': network_status,
                'public_ip': public_ip,
                'domain': self.domain,
                'domain_ip': domain_ip,
                'ip_match': ip_match,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Systemstatus: {e}")
            raise