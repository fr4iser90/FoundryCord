import psutil
import platform
import aiohttp
import asyncio
import os
import subprocess
import logging
from datetime import datetime, timedelta
import docker
import socket
import shutil
import time

from dotenv import load_dotenv

# Logger konfigurieren
logger = logging.getLogger('homelab_bot')

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

async def collect_system_data():
    """Sammelt alle Systemdaten und gibt sie als Dictionary zurück"""
    logger.info("Sammle Systemdaten...")
    
    data = {}
    
    # Basis-Systemdaten
    data['cpu'] = psutil.cpu_percent(interval=1)
    data['memory'] = psutil.virtual_memory()
    data['swap'] = psutil.swap_memory()
    data['disk'] = psutil.disk_usage('/')
    data['platform'] = platform.system()
    data['release'] = platform.release()
    data['domain'] = DOMAIN
    
    logger.info("Basis-Systemdaten gesammelt, sammle erweiterte Daten...")
    
    # Erweiterte Daten parallel sammeln
    tasks = [
        fetch_public_ip(),
        get_system_uptime(),
        get_cpu_temperature(),
        get_docker_status(),
        get_network_stats(),
        get_ssh_attempts(),
        check_services_status(),
        get_disk_usage_all()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Ergebnisse dem Daten-Dictionary hinzufügen
    data['public_ip'] = results[0] if not isinstance(results[0], Exception) else "N/A"
    data['uptime'] = results[1] if not isinstance(results[1], Exception) else "N/A"
    data['cpu_temp'] = results[2] if not isinstance(results[2], Exception) else "N/A"
    
    if not isinstance(results[3], Exception):
        data['docker_running'], data['docker_errors'], data['docker_details'] = results[3]
    else:
        data['docker_running'], data['docker_errors'], data['docker_details'] = "N/A", "N/A", "Docker nicht verfügbar"
    
    if not isinstance(results[4], Exception):
        data['net_admin'], data['net_public'] = results[4]
    else:
        data['net_admin'], data['net_public'] = "N/A", "N/A"
    
    if not isinstance(results[5], Exception):
        data['ssh_attempts'], data['last_ssh_ip'] = results[5]
    else:
        data['ssh_attempts'], data['last_ssh_ip'] = "N/A", "N/A"
    
    data['services'] = results[6] if not isinstance(results[6], Exception) else {}
    data['disk_details'] = results[7] if not isinstance(results[7], Exception) else "Keine Festplatten gefunden"
    
    # Entferne die Docker-Stats-Funktion vorerst
    # Wir werden später eine bessere Lösung implementieren
    
    return data

# Hier müssen alle Hilfsfunktionen aus dem ursprünglichen system_status_task.py eingefügt werden

async def fetch_public_ip():
    """Holt die öffentliche IP-Adresse asynchron."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.ipify.org?format=json") as resp:
                data = await resp.json()
                return data.get("ip", "N/A")
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der öffentlichen IP: {e}")
            return "N/A"

async def get_system_uptime():
    """Ermittelt die Systemlaufzeit."""
    try:
        # Für Linux-Systeme
        if platform.system() == "Linux":
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_time = timedelta(seconds=uptime_seconds)
                
                # Formatierung für bessere Lesbarkeit
                days = uptime_time.days
                hours, remainder = divmod(uptime_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                if days > 0:
                    return f"{days} Tage, {hours} Stunden, {minutes} Minuten"
                else:
                    return f"{hours} Stunden, {minutes} Minuten"
        
        # Für Windows-Systeme
        elif platform.system() == "Windows":
            uptime_ms = psutil.boot_time()
            uptime_seconds = (datetime.now().timestamp() - uptime_ms)
            uptime_time = timedelta(seconds=uptime_seconds)
            
            days = uptime_time.days
            hours, remainder = divmod(uptime_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days} Tage, {hours} Stunden, {minutes} Minuten"
            else:
                return f"{hours} Stunden, {minutes} Minuten"
        
        # Für andere Systeme
        else:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_time = timedelta(seconds=uptime_seconds)
            
            days = uptime_time.days
            hours, remainder = divmod(uptime_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days} Tage, {hours} Stunden, {minutes} Minuten"
            else:
                return f"{hours} Stunden, {minutes} Minuten"
    
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln der Uptime: {e}")
        return "Unbekannt"

async def get_cpu_temperature():
    """Ermittelt die CPU-Temperatur, falls verfügbar."""
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:  # Für Raspberry Pi
                temp = temps['cpu_thermal'][0].current
            else:
                # Erster verfügbarer Sensor
                for sensor_name, sensor_readings in temps.items():
                    if sensor_readings:
                        temp = sensor_readings[0].current
                        break
                else:
                    return "N/A"
            return temp
        else:
            return "N/A"
    except Exception as e:
        logger.error(f"Fehler bei der Temperaturmessung: {e}")
        return "N/A"

async def get_docker_status():
    """Holt Docker-Container Status mit tatsächlichen Daten oder Fallback."""
    try:
        # Versuche zuerst mit der Docker-API
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        running = 0
        errors = 0
        details = ""
        
        for container in containers:
            name = container.name
            status = container.status
            
            if status == "running":
                running += 1
                details += f"{name}: ✅ Running\n"
            elif status in ["exited", "dead", "created"]:
                errors += 1
                details += f"{name}: ❌ {status.capitalize()}\n"
            else:
                details += f"{name}: ⚠️ {status.capitalize()}\n"
        
        return running, errors, details
    except Exception as docker_api_error:
        logger.warning(f"Docker API nicht verfügbar: {docker_api_error}")
        
        # Fallback: Docker über Kommandozeile
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}: {{.Status}}"],
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.strip().split('\n')
            running = sum(1 for line in lines if "Up " in line)
            errors = sum(1 for line in lines if "Exited" in line)
            
            return running, errors, result.stdout
        except Exception as cmd_error:
            logger.error(f"Docker Kommandozeile nicht verfügbar: {cmd_error}")
            return "N/A", "N/A", "Docker nicht verfügbar"

async def get_network_stats():
    """Ermittelt Netzwerkstatistiken."""
    try:
        # Netzwerkschnittstellen abrufen
        net_io = psutil.net_io_counters(pernic=True)
        
        # Hauptschnittstelle finden (die mit dem meisten Traffic)
        main_interface = max(net_io.items(), key=lambda x: x[1].bytes_sent + x[1].bytes_recv)[0]
        
        # Detaillierte Informationen für Admins
        admin_text = "Netzwerkschnittstellen:\n"
        for interface, stats in net_io.items():
            # Konvertiere Bytes in MB
            sent_mb = stats.bytes_sent / (1024 * 1024)
            recv_mb = stats.bytes_recv / (1024 * 1024)
            admin_text += f"{interface}: ↑ {sent_mb:.2f} MB | ↓ {recv_mb:.2f} MB\n"
        
        # Vereinfachte Informationen für Public
        main_stats = net_io[main_interface]
        sent_mb = main_stats.bytes_sent / (1024 * 1024)
        recv_mb = main_stats.bytes_recv / (1024 * 1024)
        public_text = f"↑ {sent_mb:.2f} MB | ↓ {recv_mb:.2f} MB"
        
        return admin_text, public_text
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Netzwerkstatistiken: {e}")
        return "Netzwerkstatistiken nicht verfügbar", "Nicht verfügbar"

async def get_ssh_attempts():
    """Ermittelt fehlgeschlagene SSH-Anmeldeversuche."""
    try:
        if platform.system() != "Linux":
            return "N/A (nur Linux)", "N/A"
        
        # Prüfe, ob die auth.log existiert
        log_files = [
            "/var/log/auth.log",       # Debian/Ubuntu
            "/var/log/secure",         # RHEL/CentOS
            "/var/log/audit/audit.log" # Einige Systeme
        ]
        
        log_file = next((f for f in log_files if os.path.exists(f)), None)
        
        if not log_file:
            return "Log nicht gefunden", "N/A"
        
        # Suche nach fehlgeschlagenen Anmeldeversuchen
        cmd = f"grep 'Failed password' {log_file} | wc -l"
        attempts = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        
        # Letzte IP-Adresse ermitteln
        ip_cmd = f"grep 'Failed password' {log_file} | tail -1 | grep -oE '([0-9]{{1,3}}\.?){{4}}'"
        try:
            last_ip = subprocess.check_output(ip_cmd, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            last_ip = "Keine"
        
        return attempts, last_ip
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der SSH-Versuche: {e}")
        return "N/A", "N/A"

async def check_services_status():
    """Überprüft den Status wichtiger Dienste."""
    services = {}
    
    # Lokale Dienste (Port-basiert)
    local_services = [
        {"name": "🔐 SSH", "port": 22},
        # Weitere lokale Dienste hier hinzufügen
    ]
    
    # Externe Dienste (URL-basiert)
    external_services = [
        {"name": "☁️ Owncloud", "url": f"https://owncloud.{DOMAIN}"},
        {"name": "📊 Grafana", "url": f"https://grafana.{DOMAIN}"},
        {"name": "📝 Nextcloud", "url": f"https://nextcloud.{DOMAIN}"},
        {"name": "🔄 Portainer", "url": f"https://portainer.{DOMAIN}"},
        {"name": "📁 Fileserver", "url": f"https://files.{DOMAIN}"},
        # Weitere externe Dienste hier hinzufügen
    ]
    
    # Lokale Dienste überprüfen
    for service in local_services:
        try:
            # Für SSH speziell prüfen wir, ob der Prozess läuft
            if service["port"] == 22:
                # Prüfen, ob der SSH-Prozess läuft
                ssh_running = False
                try:
                    # Für Linux
                    result = subprocess.run(["pgrep", "sshd"], capture_output=True, text=True)
                    ssh_running = result.returncode == 0
                except:
                    # Fallback: Versuche, den Port zu prüfen
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    ssh_running = sock.connect_ex(('127.0.0.1', 22)) == 0
                    sock.close()
                
                services[service["name"]] = "✅ Online" if ssh_running else "❌ Offline"
            else:
                # Normale Port-Überprüfung für andere Dienste
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
    
    # Externe Dienste überprüfen
    async with aiohttp.ClientSession() as session:
        for service in external_services:
            try:
                async with session.get(service["url"], timeout=5, ssl=False) as response:
                    if response.status < 400:  # HTTP 200-399 gelten als erfolgreich
                        services[service["name"]] = "✅ Online"
                    elif response.status == 401 or response.status == 403:
                        services[service["name"]] = "🔒 Geschützt"  # Authentifizierung erforderlich
                    else:
                        services[service["name"]] = f"❌ Status {response.status}"
            except asyncio.TimeoutError:
                services[service["name"]] = "⏱️ Timeout"
            except Exception as e:
                logger.debug(f"Fehler bei {service['name']}: {str(e)}")
                services[service["name"]] = "❌ Offline"
    
    return services

async def get_disk_usage_all():
    """Ermittelt die Festplattennutzung aller Laufwerke."""
    try:
        partitions = psutil.disk_partitions()
        result = "```\n"
        
        for partition in partitions:
            # Überspringe spezielle Dateisysteme
            if any(skip in partition.mountpoint for skip in [
                '/etc/', '/proc/', '/sys/', '/dev/', '/run/', '/docker/', 
                '/snap/', '/boot/', '/var/lib/docker'
            ]):
                continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                # Konvertiere Bytes in GB
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                
                # Formatiere die Ausgabe
                result += f"{partition.mountpoint}: {used_gb:.1f}/{total_gb:.1f} GB ({usage.percent}%)\n"
            except PermissionError:
                continue
        
        result += "```"
        return result
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Festplattennutzung: {e}")
        return "Festplattennutzung nicht verfügbar"