from typing import Optional, Dict, Any
import nextcord
from datetime import datetime
from infrastructure.logging import logger

class GeneralDashboardUI:
    def __init__(self, bot):
        self.bot = bot
        self.message: Optional[nextcord.Message] = None
        self.channel: Optional[nextcord.TextChannel] = None
        self.service = None

    def set_service(self, service):
        """Dependency Injection für den Service"""
        self.service = service
        logger.debug("Service injected into GeneralDashboard")

    async def setup(self):
        """Initialisiert das Dashboard"""
        try:
            # Channel aus der Config holen
            from infrastructure.config.channel_config import ChannelConfig
            channel_id = await ChannelConfig.get_channel_id('general')
            self.channel = self.bot.get_channel(channel_id)
            
            if not self.channel:
                logger.error("General channel not found")
                return
            
            await self.refresh()
            logger.info("General Dashboard setup completed")
            
        except Exception as e:
            logger.error(f"Error in General Dashboard setup: {e}")
            raise

    async def create_embed(self) -> nextcord.Embed:
        """Erstellt das Haupt-Embed mit Daten vom Service"""
        if not self.service:
            logger.error("No service available for GeneralDashboard")
            return self._create_error_embed()

        try:
            system_status = await self.service.get_system_status()
            
            embed = nextcord.Embed(
                title="🏠 HomeLab Dashboard",
                description="Willkommen im HomeLab! Hier findest du alle wichtigen Informationen.",
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            
            # Server Status aus dem Service
            cpu = system_status['cpu_usage']
            memory = system_status['memory_usage']
            disk = system_status['disk_usage']
            network = system_status['network_status']
            
            embed.add_field(
                name="🖥️ Server Status",
                value=f"```\n"
                      f"CPU: {cpu:.1f}% | RAM: {memory['used']:.1f}GB/{memory['total']:.1f}GB\n"
                      f"Storage: {disk['used']:.1f}GB/{disk['total']:.1f}TB\n"
                      f"Network: {'🟢 Online' if network['up'] else '🔴 Offline'} | "
                      f"Latenz: {network['latency']:.1f}ms```",
                inline=False
            )
            
            # Aktive Services
            embed.add_field(
                name="🚀 Aktive Services",
                value="• **Gameserver**: 2/3 online\n"
                      "• **Monitoring**: Aktiv\n"
                      "• **Backups**: Letzte Sicherung vor 2h",
                inline=True
            )
            
            # Quick Links
            embed.add_field(
                name="🔗 Quick Links",
                value="• [Projekt Dashboard]()\n"
                      "• [Service Status]()\n"
                      "• [Wiki]()",
                inline=True
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            return self._create_error_embed()

    def _create_error_embed(self) -> nextcord.Embed:
        """Erstellt ein Fehler-Embed wenn etwas schief geht"""
        return nextcord.Embed(
            title="⚠️ Dashboard Error",
            description="Entschuldigung, die Dashboard-Daten konnten nicht geladen werden.",
            color=0xff0000
        )

    def create_view(self) -> nextcord.ui.View:
        """Erstellt die View mit Buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Refresh Button
        refresh_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Aktualisieren",
            emoji="🔄",
            custom_id="refresh_general",
            row=0
        )
        refresh_btn.callback = self.on_refresh
        view.add_item(refresh_btn)
        
        # Service Status Button
        status_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Service Status",
            emoji="📊",
            custom_id="show_status",
            row=0
        )
        status_btn.callback = self.on_status
        view.add_item(status_btn)
        
        return view

    async def refresh(self):
        """Aktualisiert das Dashboard"""
        if self.message:
            await self.message.edit(embed=await self.create_embed(), view=self.create_view())
        else:
            self.message = await self.channel.send(embed=await self.create_embed(), view=self.create_view())

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler für den Refresh Button"""
        await self.refresh()
        await interaction.response.send_message("Dashboard wurde aktualisiert!", ephemeral=True)

    async def on_status(self, interaction: nextcord.Interaction):
        """Handler für den Status Button"""
        # Hier könnte eine detailliertere Status-Ansicht implementiert werden
        await interaction.response.send_message("Service Status wird implementiert!", ephemeral=True)