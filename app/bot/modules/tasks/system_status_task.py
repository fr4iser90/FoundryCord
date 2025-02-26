# modules/monitoring/system_status_task.py
import nextcord
import psutil
import aiohttp
import socket
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from core.config.users import ADMINS, GUESTS

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
    return f"{bars} {percent}%"

def get_system_color(cpu, memory, disk):
    """Bestimmt die Embed-Farbe basierend auf Auslastung"""
    if cpu > 80 or memory > 90 or disk > 90:
        return 0xff0000  # Rot
    elif cpu > 60 or memory > 75 or disk > 75:
        return 0xffa500  # Orange
    return 0x00ff00      # Grün

async def get_docker_status():
    """Holt Docker-Container Status (Beispiel)"""
    try:
        # Hier echte Docker-Implementierung einfügen
        return "15/15", "0"
    except Exception as e:
        print(f"Docker-Fehler: {e}")
        return "N/A", "N/A"

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
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            public_ip = await fetch_public_ip()
            
            try:
                temp = psutil.sensors_temperatures()['coretemp'][0].current
            except Exception as temp_error:
                print(f"Temperaturmessung fehlgeschlagen: {temp_error}")
                temp = "N/A"
            docker_running, docker_errors = await get_docker_status()  
            # Öffentliches Embed erstellen
            public_embed = nextcord.Embed(
                title="🏠 HomeLab Status - Public",
                color=get_system_color(cpu, memory.percent, disk.percent),
                timestamp=datetime.now()
            ).add_field(
                name="Dienste",
                value="🌐 Webseite: Online\n📂 Fileserver: Online\n🎮 Game Server: Offline",
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
            ).set_footer(text="Aktualisiert")

            # Admin Embed erstellen
            admin_embed = nextcord.Embed(
                title="🔒 HomeLab Status - Admin",
                color=0x7289da,
                timestamp=datetime.now()
            ).add_field(
                name="Hardware",
                value=f"CPU: {cpu}% ({temp}°C)\nRAM: {memory.used/1024**3:.1f}/{memory.total/1024**3:.1f} GB\nDisk: {disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB\nNET: ▼12Mbps ▲4Mbps",
                inline=True
            ).add_field(
                name="Sicherheit",
                value=f"🔥 Firewall: Aktiv\n🔐 SSH-Versuche: 3\n🌍 IP: {public_ip}",
                inline=True
            ).add_field(
                name="Services",
                value=(
                    "```ini\n"
                    f"[Docker]\n"
                    f"Running: {docker_running}\n"
                    f"Errors: {docker_errors}\n"
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