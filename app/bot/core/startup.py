# @/app/bot/core/startup.py
import os
import nextcord
from modules.monitoring.system_status_task import system_status_task

# Event handler für on_ready
def setup_bot(bot):
    """Setzt den Eventhandler für on_ready."""
    @bot.event
    async def on_ready():
        print(f'Bot ist eingeloggt als {bot.user}')
        print(f'Befehle: {bot.commands}')

        # Kanal-ID aus den Umgebungsvariablen lesen
        discord_homelab_channel_id = int(os.getenv('DISCORD_HOMELAB_CHANNEL', '0'))  # Standardwert: 0 (falls nicht gesetzt)

        if discord_homelab_channel_id:
            channel = bot.get_channel(discord_homelab_channel_id)
            if channel:
                bot.loop.create_task(system_status_task(bot, discord_homelab_channel_id))
                # await channel.send("Bot ist bereit!")
            else:
                print(f"Kanal mit der ID {discord_homelab_channel_id} wurde nicht gefunden.")
        else:
            print("DISCORD_HOMELAB_CHANNEL ist nicht in den Umgebungsvariablen gesetzt.")