import nextcord
from datetime import datetime
import logging
import psutil
from .collectors.hardware import get_hardware_info  

logger = logging.getLogger(__name__)

class StatusView(nextcord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=None)  # Kein Timeout für die Buttons
        self.data = data

    @nextcord.ui.button(label="🖥️ Hardware", style=nextcord.ButtonStyle.primary)
    async def hardware_info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Hardware Informationen anzeigen"""
        try:
            hw_info = await get_hardware_info()  # Direkt die Hardware-Infos holen
            logger.debug(f"Hardware Info für Anzeige: {hw_info}")

            # CPU Temperatur aus Sensoren
            cpu_temp = hw_info.get('temp_coretemp_Package id 0', 'N/A')
            
            message = [
                "```ini",
                "[CPU Information]",
                f"Modell: {hw_info.get('cpu_model', 'N/A')}",
                f"Kerne/Threads: {hw_info.get('cpu_cores', 'N/A')}/{hw_info.get('cpu_threads', 'N/A')}",
                f"Takt: {hw_info.get('cpu_freq_current', 'N/A')} (Min: {hw_info.get('cpu_freq_min', 'N/A')}, Max: {hw_info.get('cpu_freq_max', 'N/A')})",
                f"Auslastung: {psutil.cpu_percent()}% bei {cpu_temp}°C",
                f"Stromverbrauch: {hw_info.get('cpu_power', 'N/A')}",
                "",
                "[System Sensoren]",
                *[f"{key.replace('temp_', '')}: {value}°C" for key, value in hw_info.items() if key.startswith('temp_')],
                "",
                "[RAM Information]",
                f"Gesamt: {hw_info.get('ram_total', 0):.1f} GB",
                f"Verwendet: {hw_info.get('ram_used', 0):.1f} GB ({hw_info.get('ram_percent', 0)}%)",
                f"Swap: {hw_info.get('swap_used', 0):.1f}/{hw_info.get('swap_total', 0):.1f} GB",
                "",
                "[System Information]",
                f"Plattform: {hw_info.get('system_platform', 'N/A')}",
                f"Version: {hw_info.get('system_version', 'N/A')}",
                f"Hostname: {hw_info.get('system_hostname', 'N/A')}",
                f"Uptime: {hw_info.get('system_uptime', 'N/A')}",
                "",
                "[Power Status]",
                *[f"{key}: {value}" for key, value in hw_info.items() if key.startswith(('power_', 'battery_'))],
                "",
                "[Netzwerk-Adapter]",
                hw_info.get('network_adapters', 'Keine Netzwerk-Informationen verfügbar'),
                "```"
            ]

            # Leere Sektionen entfernen
            filtered_message = []
            current_section = []
            
            for line in message:
                if line.startswith('[') and line.endswith(']'):
                    if current_section and len(current_section) > 1:
                        filtered_message.extend(current_section)
                    current_section = [line]
                else:
                    current_section.append(line)
                
            if current_section and len(current_section) > 1:
                filtered_message.extend(current_section)

            await interaction.response.send_message('\n'.join(filtered_message), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Hardware-Info: {e}")
            await interaction.response.send_message(
                "```ini\n[Fehler]\nKonnte Hardware-Informationen nicht abrufen.```", 
                ephemeral=True
            )

    @nextcord.ui.button(label="🌐 Netzwerk", style=nextcord.ButtonStyle.primary)
    async def network_info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"```\n{self.data['net_admin']}\n```",
            ephemeral=True
        )

    @nextcord.ui.button(label="🔄 Docker", style=nextcord.ButtonStyle.primary)
    async def docker_info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "```ini\n"
            f"[Status]\n"
            f"Running: {self.data['docker_running']}\n"
            f"Errors: {self.data['docker_errors']}\n\n"
            f"[Container]\n{self.data['docker_details']}\n"
            "```",
            ephemeral=True
        )

def create_admin_embed(data):
    """Erstellt das Admin-Status-Embed mit detaillierten Informationen und Buttons"""
    admin_embed = nextcord.Embed(
        title="🔒 HomeLab Status - Admin",
        description=f"System: {data['platform']} {data['release']} | Uptime: {data['uptime']}",
        color=0x7289da,
        timestamp=datetime.now()
    ).add_field(
        name="Quick Overview",
        value=(
            f"CPU: {data['cpu']}% ({data['cpu_temp']}°C)\n"
            f"RAM: {data['memory'].used/1024**3:.1f}/{data['memory'].total/1024**3:.1f} GB ({data['memory'].percent}%)\n"
            f"Swap: {data['swap'].used/1024**3:.1f}/{data['swap'].total/1024**3:.1f} GB\n"
            f"Docker: {data['docker_running']} Running, {data['docker_errors']} Errors"
        ),
        inline=False
    ).add_field(
        name="Sicherheit",
        value=(
            f"🔥 Firewall: Aktiv\n"
            f"🔐 SSH-Versuche: {data['ssh_attempts']}\n"
            f"🔍 Letzte IP: {data['last_ssh_ip']}\n"
            f"🌍 Öffentliche IP: {data['public_ip']}"
        ),
        inline=False
    ).set_footer(text=f"Domain: {data['domain']} | IP: {data['public_ip']}")
    
    view = StatusView(data)
    return admin_embed, view