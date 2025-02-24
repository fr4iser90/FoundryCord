# modules/monitoring/system_status_task.py
import nextcord
import psutil
import aiohttp
import socket
import asyncio
import os
from dotenv import load_dotenv
from config.users import ADMINS

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

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

async def system_status_task(bot, channel_id):
    """Task, der alle 30 Minuten den Systemstatus in einem privaten Thread postet."""
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    
    if not channel:
        print(f"Kanal mit ID {channel_id} nicht gefunden.")
        return

    # Bestehenden "System Status"-Thread suchen
    thread = next((t for t in channel.threads if t.name == "System Status"), None)
    
    if not thread:
        # Neuen Thread erstellen, falls keiner existiert
        thread = await channel.create_thread(
            name="System Status",
            auto_archive_duration=60,
            reason="Automatische Updates"
        )

        # Admins nur einmalig hinzufügen
        for admin_id in ADMINS.values():
            admin = channel.guild.get_member(int(admin_id))
            if admin:
                try:
                    await thread.add_user(admin)
                except Exception as e:
                    print(f"Fehler beim Hinzufügen von Admin {admin_id}: {e}")

    while True:
        # Alle Nachrichten im Thread löschen, bevor die neue gesendet wird
        try:
            async for msg in thread.history(limit=100):
                await msg.delete()
        except Exception as e:
            print(f"Fehler beim Bereinigen des Threads: {e}")

        # Systemstatus abrufen
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        public_ip = await fetch_public_ip()

        # Domain-IP vergleichen
        try:
            domain_ip = socket.gethostbyname(DOMAIN) if DOMAIN else "N/A"
            ip_match = "✅" if public_ip == domain_ip else "❌"
        except Exception as e:
            print(f"Fehler beim Auflösen der Domain {DOMAIN}: {e}")
            domain_ip = "N/A"
            ip_match = "❌"

        # Neue Nachricht senden
        await thread.send(
            f"**System Status**\n"
            f"CPU: {cpu}%\n"
            f"RAM: {memory}%\n"
            f"Disk: {disk}%\n"
            f"IP: {public_ip}\n"
            f"Domain: {DOMAIN} ({domain_ip}) {ip_match}"
        )

        await asyncio.sleep(1800)  # 30 Minuten warten
