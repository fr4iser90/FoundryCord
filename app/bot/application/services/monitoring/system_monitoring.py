import psutil
import requests
import socket
from dotenv import load_dotenv
import os
from app.bot.utils.http_client import http_client
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.config.feature_flags import DOMAIN, OFFLINE_MODE, ENABLE_DOMAIN_CHECKS

# Load environment variables from .env file
load_dotenv()

# Get DOMAIN from environment variable
DOMAIN = os.getenv('DOMAIN')

# Check if DOMAIN is loaded correctly
if not DOMAIN:
    print("Warning: DOMAIN not found in environment variables. Please check your .env file.")

class SystemMonitoringService:
    """Service class for system monitoring operations"""
    
    def __init__(self, bot):
        self.bot = bot

    async def get_full_system_status(self):
        """Gets detailed system information"""
        try:
            # CPU, Memory, Disk usage
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Fetch Public IPv4 address (only if not in offline mode)
            if not OFFLINE_MODE:
                try:
                    public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
                except requests.RequestException:
                    public_ip = "Unable to fetch public IP"
            else:
                public_ip = "127.0.0.1 (Offline Mode)"

            # Domain checks only if enabled
            if ENABLE_DOMAIN_CHECKS:
                try:
                    domain_ip = socket.gethostbyname(DOMAIN)
                    ip_match = "matches" if public_ip == domain_ip else "does not match"
                except socket.gaierror:
                    domain_ip = "Unable to resolve domain"
                    ip_match = "N/A"
            else:
                domain_ip = "Domain checks disabled"
                ip_match = "N/A (Offline Mode)"
                
            return {
                "cpu_percent": cpu_percent,
                "memory": memory,
                "disk": disk,
                "public_ip": public_ip,
                "domain": DOMAIN,
                "domain_ip": domain_ip,
                "ip_match": ip_match
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Systemstatus: {e}")
            raise

    async def get_basic_system_status(self):
        """Gets basic system information (CPU, memory, disk)"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory": memory,
                "disk": disk
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Systemstatus: {e}")
            raise

    async def get_public_ip(self):
        """Gets the public IP address"""
        try:
            public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
            return public_ip
        except requests.RequestException:
            logger.error("Unable to fetch public IP")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der öffentlichen IP: {e}")
            raise

async def setup(bot):
    """Setup function for the system monitoring service"""
    try:
        service = SystemMonitoringService(bot)
        # Register the service on the bot so commands can access it
        bot.system_monitoring_service = service
        logger.info("System monitoring service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize system monitoring service: {e}")
        raise