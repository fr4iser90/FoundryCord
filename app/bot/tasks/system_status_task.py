# modules/monitoring/system_status_task.py
import nextcord
import psutil
import aiohttp
import socket
import asyncio
import os
import subprocess
import platform
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.config.users import ADMINS, GUESTS
import docker
import shutil

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

# Hilfsfunktionen
async def fetch_public_ip():
    """Holt die öffentliche IP-Adresse asynchron."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.ipify.org?format=json") as resp:
                data = await resp.json()
                return data.get("ip", "N/A")
        except Exception as e:
            print(f"Fehler beim Abrufen der öffentlichen IP: {e}")
            return "N/A"

def progress_bar(percent):
    """Erstellt einen Text-basierten Fortschrittsbalken"""
    bars = "█" * int(percent/10) + "░" * (10 - int(percent/10))
    return f"{bars} {percent:.1f}%"

def get_system_color(cpu, memory, disk):
    """Bestimmt die Embed-Farbe basierend auf Auslastung"""
    if cpu > 80 or memory > 90 or disk > 90:
        return 0xff0000  # Rot 
    elif cpu > 60 or memory > 75 or disk > 75:
        return 0xffa500  # Orange
    return 0x00ff00      # Grün

async def get_docker_status():
    """Holt Docker-Container Status mit tatsächlichen Daten oder Fallback"""
    try:
        # Versuche zuerst mit der Docker-API
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        running = len([c for c in containers if c.status == 'running'])
        total = len(containers)
        errors = len([c for c in containers if c.status == 'exited' or c.status == 'dead'])
        
        # Detaillierte Container-Informationen
        container_details = []
        for c in containers:
            if c.status == 'running':
                status_emoji = "🟢"
            elif c.status == 'exited':
                status_emoji = "🔴"
            else:
                status_emoji = "🟠"
                
            container_details.append(f"{status_emoji} {c.name} ({c.status})")
        
        # Nur die ersten 10 Container anzeigen, um Platz zu sparen
        if len(container_details) > 10:
            container_details = container_details[:10]
            container_details.append(f"... und {len(containers) - 10} weitere")
            
        return f"{running}/{total}", str(errors), "\n".join(container_details)
    except Exception as e:
        print(f"Docker-API-Fehler: {e}")
        
        # Fallback: Verwende docker ps über subprocess
        try:
            # Prüfe, ob docker-Befehl verfügbar ist
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}} ({{.Status}})"], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                containers = [c for c in containers if c]  # Leere Zeilen entfernen
                
                # Zähle laufende Container (vereinfacht)
                running = len([c for c in containers if "Up" in c])
                total = len(containers)
                
                return f"{running}/{total}", "N/A", "\n".join(containers[:10])
            else:
                raise Exception("Docker-Befehl fehlgeschlagen")
        except Exception as sub_e:
            print(f"Docker-Subprocess-Fehler: {sub_e}")
            return "N/A", "N/A", "Docker nicht verfügbar"

async def get_network_stats():
    """Holt detaillierte Netzwerkstatistiken mit Maximalwerten"""
    try:
        # Konfigurierbare Maximalwerte (in Mbps)
        max_download = 250  # 250 Mbps Download
        max_upload = 40     # 40 Mbps Upload
        
        net_io = psutil.net_io_counters()
        
        # Bytes in MB umrechnen
        recv_mb = net_io.bytes_recv / 1024**2
        sent_mb = net_io.bytes_sent / 1024**2
        
        # Aktuelle Geschwindigkeit (erfordert zwei Messungen)
        await asyncio.sleep(1)
        net_io_new = psutil.net_io_counters()
        
        recv_speed = (net_io_new.bytes_recv - net_io.bytes_recv) / 1024**2 * 8  # Mbps
        sent_speed = (net_io_new.bytes_sent - net_io.bytes_sent) / 1024**2 * 8  # Mbps
        
        # Prozentsatz der Maximalgeschwindigkeit berechnen
        recv_percent = min(100, recv_speed / max_download * 100)
        sent_percent = min(100, sent_speed / max_upload * 100)
        
        # Fortschrittsbalken für Netzwerkauslastung
        recv_bar = progress_bar(recv_percent)
        sent_bar = progress_bar(sent_percent)
        
        # Formatierte Ausgabe
        speed_text = f"▼{recv_speed:.1f}/{max_download}Mbps ({recv_percent:.0f}%)\n▲{sent_speed:.1f}/{max_upload}Mbps ({sent_percent:.0f}%)"
        total_text = f"▼{recv_mb:.1f}MB ▲{sent_mb:.1f}MB"
        
        # Detaillierte Ausgabe für Admin-Panel
        admin_text = (
            f"{total_text}\n"
            f"Download: {recv_bar}\n"
            f"Upload: {sent_bar}"
        )
        
        # Einfachere Ausgabe für Public-Panel
        public_text = f"▼{recv_speed:.1f}Mbps ▲{sent_speed:.1f}Mbps"
        
        return admin_text, public_text
    except Exception as e:
        print(f"Netzwerk-Fehler: {e}")
        return "N/A", "N/A"

async def get_system_uptime():
    """Holt die System-Uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        else:
            return f"{hours}h {minutes}m {seconds}s"
    except Exception as e:
        print(f"Uptime-Fehler: {e}")
        return "N/A"

async def get_ssh_attempts():
    """Zählt fehlgeschlagene SSH-Anmeldeversuche aus dem Auth-Log"""
    try:
        if os.path.exists('/var/log/auth.log'):
            # Linux-Systeme mit auth.log
            cmd = "grep 'Failed password' /var/log/auth.log | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            count = result.stdout.strip()
            
            # Letzte IP-Adresse
            ip_cmd = "grep 'Failed password' /var/log/auth.log | tail -1 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'"
            ip_result = subprocess.run(ip_cmd, shell=True, capture_output=True, text=True)
            last_ip = ip_result.stdout.strip() or "Keine"
            
            return count, last_ip
        else:
            # Fallback für andere Systeme
            return "N/A", "N/A"
    except Exception as e:
        print(f"SSH-Log-Fehler: {e}")
        return "N/A", "N/A"

async def get_disk_usage_all():
    """Holt Festplattennutzung für alle Laufwerke"""
    try:
        disk_info = []
        seen_devices = set()  # Um Duplikate zu vermeiden
        
        # Hauptpartition zuerst anzeigen
        root_usage = psutil.disk_usage('/')
        disk_info.append(f"/ (Root): {root_usage.used/1024**3:.1f}/{root_usage.total/1024**3:.1f}GB ({root_usage.percent}%)")
        
        # Andere physische Partitionen hinzufügen (keine Container-Mounts)
        for part in psutil.disk_partitions(all=False):
            # Überspringe Root-Partition (bereits hinzugefügt)
            if part.mountpoint == '/':
                continue
                
            # Überspringe Container-Mounts und virtuelle Dateisysteme
            if any(skip in part.mountpoint for skip in [
                '/etc/', '/proc/', '/sys/', '/dev/', '/run/', '/docker/', 
                '/var/lib/docker', '/snap/', '/tmp/'
            ]):
                continue
                
            # Überspringe temporäre Dateisysteme
            if part.fstype in ('tmpfs', 'devtmpfs', 'devfs', 'overlay', 'aufs'):
                continue
                
            # Überspringe bereits gesehene Geräte
            if part.device in seen_devices:
                continue
                
            seen_devices.add(part.device)
            
            try:
                usage = psutil.disk_usage(part.mountpoint)
                # Nur Laufwerke mit mehr als 1GB anzeigen
                if usage.total > 1024**3:  # Größer als 1GB
                    disk_info.append(f"{part.mountpoint}: {usage.used/1024**3:.1f}/{usage.total/1024**3:.1f}GB ({usage.percent}%)")
            except (PermissionError, OSError):
                # Überspringe Laufwerke, auf die wir keinen Zugriff haben
                continue
        
        return "\n".join(disk_info) if disk_info else "Keine Festplatten gefunden"
    except Exception as e:
        print(f"Disk-Fehler: {e}")
        return "Fehler beim Abrufen der Festplatteninformationen"

async def check_services_status():
    """Prüft den Status wichtiger Dienste"""
    services = {
        "🌐 Webserver": ["nginx", "apache2"],
        "📂 Fileserver": ["smbd", "nfs"],
        "🔒 VPN": ["wireguard", "openvpn"],
        "🗄️ Datenbank": ["mysql", "postgresql", "mongodb"],
        "🐳 Docker": ["docker"]
    }
    
    results = {}
    
    for name, service_list in services.items():
        status = "Offline"
        for service in service_list:
            try:
                if platform.system() == "Linux":
                    cmd = f"systemctl is-active {service}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if "active" in result.stdout:
                        status = "Online"
                        break
                else:
                    # Einfache Prozessprüfung für andere Betriebssysteme
                    for proc in psutil.process_iter(['name']):
                        if service.lower() in proc.info['name'].lower():
                            status = "Online"
                            break
            except Exception:
                pass
        
        results[name] = status
    
    return results

async def send_embed_with_retry(channel, embed, max_retries=3):
    """Sendet ein Embed mit Wiederholungsversuchen"""
    for attempt in range(max_retries):
        try:
            await channel.purge(limit=100)
            await channel.send(embed=embed)
            return True
        except nextcord.HTTPException as e:
            print(f"Versuch {attempt+1}/{max_retries} fehlgeschlagen: {e}")
            await asyncio.sleep(5)
    return False

# Haupt-Task
async def system_status_task(bot, channel_id):
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    
    if not channel:
        print(f"Kanal mit ID {channel_id} nicht gefunden.")
        return

    # Debug: Berechtigungen prüfen
    print(f"Channel Permissions: {channel.permissions_for(channel.guild.me)}")

    # Threads erstellen oder suchen
    try:
        public_thread = next((t for t in channel.threads if t.name == "Public Status"), None)
        if not public_thread:
            public_thread = await channel.create_thread(
                name="Public Status",
                auto_archive_duration=1440,
                reason="Automatische Updates"
            )
            print("Public Thread erstellt")

            # Gäste hinzufügen
        for guest_id in GUESTS.values():
            try:
                guest = await channel.guild.fetch_member(int(guest_id))
                if guest:
                    await public_thread.add_user(guest)
                    print(f"Gast {guest.display_name} hinzugefügt")
                    await asyncio.sleep(1)  # Rate Limit vermeiden
            except Exception as e:
                print(f"Fehler beim Hinzufügen von Gast {guest_id}: {e}")

        admin_thread = next((t for t in channel.threads if t.name == "Admin Status"), None)
        if not admin_thread:
            admin_thread = await channel.create_thread(
                name="Admin Status",
                auto_archive_duration=1440,
                reason="Automatische Updates",
                type=nextcord.ChannelType.private_thread
            )
            print("Admin Thread erstellt")

            # Admins hinzufügen
        for admin_id in ADMINS.values():
            try:
                admin = await channel.guild.fetch_member(int(admin_id))
                if admin:
                    await admin_thread.add_user(admin)
                    print(f"Admin {admin.display_name} hinzugefügt")
                    await asyncio.sleep(1)  # Rate Limit vermeiden
            except Exception as e:
                print(f"Fehler beim Hinzufügen von Admin {admin_id}: {e}")

        # Threads reaktivieren falls archiviert
        if public_thread.archived:
            await public_thread.edit(archived=False)
            print("Public Thread reaktiviert")

        if admin_thread.archived:
            await admin_thread.edit(archived=False)
            print("Admin Thread reaktiviert")

    except Exception as e:
        print(f"Thread-Erstellung fehlgeschlagen: {e}")
        return

    while True:
        try:
            # Systemdaten sammeln
            cpu = psutil.cpu_percent(interval=1)  # 1 Sekunde Messintervall für genauere Werte
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            public_ip = await fetch_public_ip()
            uptime = await get_system_uptime()
            
            # Temperatur (wenn verfügbar)
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if 'coretemp' in temps:
                        temp = temps['coretemp'][0].current
                    elif 'cpu_thermal' in temps:  # Für Raspberry Pi
                        temp = temps['cpu_thermal'][0].current
                    else:
                        temp = list(temps.values())[0][0].current  # Erster verfügbarer Sensor
                else:
                    temp = "N/A"
            except Exception as temp_error:
                print(f"Temperaturmessung fehlgeschlagen: {temp_error}")
                temp = "N/A"
            
            # Docker-Status
            docker_running, docker_errors, docker_details = await get_docker_status()
            
            # Netzwerkstatistiken
            net_admin, net_public = await get_network_stats()
            
            # SSH-Versuche
            ssh_attempts, last_ssh_ip = await get_ssh_attempts()
            
            # Dienste-Status
            services = await check_services_status()
            services_text = "\n".join([f"{name}: {status}" for name, status in services.items()])
            
            # Festplattennutzung aller Laufwerke
            disk_details = await get_disk_usage_all()
            
            # Öffentliches Embed erstellen
            public_embed = nextcord.Embed(
                title="🏠 HomeLab Status - Public",
                description=f"System läuft seit: {uptime}",
                color=get_system_color(cpu, memory.percent, disk.percent),
                timestamp=datetime.now()
            ).add_field(
                name="Dienste",
                value=services_text,
                inline=False
            ).add_field(
                name="Auslastung",
                value=(
                    "```diff\n"
                    f"+ CPU:  {progress_bar(cpu)}\n"
                    f"+ RAM:  {progress_bar(memory.percent)}\n"
                    f"+ Disk: {progress_bar(disk.percent)}\n"
                    "```"
                ),
                inline=False
            ).add_field(
                name="Netzwerk",
                value=f"Aktuelle Geschwindigkeit: {net_public}",
                inline=False
            ).set_footer(text=f"Aktualisiert | Domain: {DOMAIN}")

            # Admin Embed erstellen
            admin_embed = nextcord.Embed(
                title="🔒 HomeLab Status - Admin",
                description=f"System: {platform.system()} {platform.release()} | Uptime: {uptime}",
                color=0x7289da,
                timestamp=datetime.now()
            ).add_field(
                name="Hardware",
                value=(
                    f"CPU: {cpu}% ({temp}°C)\n"
                    f"RAM: {memory.used/1024**3:.1f}/{memory.total/1024**3:.1f} GB ({memory.percent}%)\n"
                    f"Swap: {psutil.swap_memory().used/1024**3:.1f}/{psutil.swap_memory().total/1024**3:.1f} GB"
                ),
                inline=False
            ).add_field(
                name="Netzwerk",
                value=f"```\n{net_admin}\n```",
                inline=False
            ).add_field(
                name="Festplatten",
                value=disk_details,
                inline=False
            ).add_field(
                name="Sicherheit",
                value=(
                    f"🔥 Firewall: Aktiv\n"
                    f"🔐 SSH-Versuche: {ssh_attempts}\n"
                    f"🔍 Letzte IP: {last_ssh_ip}\n"
                    f"🌍 Öffentliche IP: {public_ip}"
                ),
                inline=False
            ).add_field(
                name="Docker Container",
                value=(
                    "```ini\n"
                    f"[Status]\n"
                    f"Running: {docker_running}\n"
                    f"Errors: {docker_errors}\n\n"
                    f"[Container]\n{docker_details}\n"
                    "```"
                ),
                inline=False
            ).set_footer(text=f"Domain: {DOMAIN} | IP: {public_ip}")

            # Embeds senden
            public_success = await send_embed_with_retry(public_thread, public_embed)
            admin_success = await send_embed_with_retry(admin_thread, admin_embed)

            if not public_success or not admin_success:
                print("Kritischer Fehler beim Senden der Statusupdates")

        except Exception as e:
            print(f"Kritischer Systemfehler: {str(e)}")
            await asyncio.sleep(60)  # Kurze Pause bei Fehlern

        await asyncio.sleep(1800)  # 30 Minuten Wartezeit