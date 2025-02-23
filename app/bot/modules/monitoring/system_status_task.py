# modules/monitoring/system_status_task.py
import nextcord
import psutil
import requests
import socket
import asyncio
import os
from dotenv import load_dotenv
from config.users import ADMINS

# Load environment variables from .env file
load_dotenv()
DOMAIN = os.getenv('DOMAIN')

async def system_status_task(bot, channel_id):
    """Task, der alle 5 Minuten den Systemstatus in einem privaten Thread postet."""
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Kanal mit ID {channel_id} nicht gefunden.")
        return

    # Thread erstellen
    thread = await channel.create_thread(
        name="System Status",
        auto_archive_duration=60,
        reason="Automatische Updates"
    )

    # Admins Zugriff gewähren
    for admin_name, admin_id in ADMINS.items():
        admin = channel.guild.get_member(int(admin_id))
        if admin:
            await thread.add_user(admin)  # Admin zum Thread hinzufügen

    # Variable zum Speichern der letzten Nachricht
    last_message = None

    while True:
        # Alte Nachricht löschen, falls vorhanden
        if last_message:
            try:
                await last_message.delete()
            except nextcord.NotFound:
                print("Die letzte Nachricht wurde bereits gelöscht.")
            except nextcord.Forbidden:
                print("Keine Berechtigung, die Nachricht zu löschen.")
            except nextcord.HTTPException as e:
                print(f"Fehler beim Löschen der Nachricht: {e}")

        # Statusdaten sammeln
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        try:
            public_ip = requests.get("https://api.ipify.org?format=json").json()['ip']
        except:
            public_ip = "N/A"

        try:
            domain_ip = socket.gethostbyname(DOMAIN) if DOMAIN else "N/A"
            ip_match = "✅" if public_ip == domain_ip else "❌"
        except:
            domain_ip = "N/A"
            ip_match = "❌"

        # Neue Nachricht senden und speichern
        last_message = await thread.send(
            f"**System Status**\n"
            f"CPU: {cpu}%\n"
            f"RAM: {memory}%\n"
            f"Disk: {disk}%\n"
            f"IP: {public_ip}\n"
            f"Domain: {DOMAIN} ({domain_ip}) {ip_match}"
        )

        await asyncio.sleep(3600)  # 5 Minuten warten