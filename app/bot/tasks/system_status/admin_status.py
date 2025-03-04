import nextcord
from datetime import datetime

class StatusView(nextcord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=None)  # Kein Timeout für die Buttons
        self.data = data

    @nextcord.ui.button(label="🖥️ Hardware", style=nextcord.ButtonStyle.primary)
    async def hardware_info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"```\nCPU: {self.data['cpu']}% ({self.data['cpu_temp']}°C)\n"
            f"RAM: {self.data['memory'].used/1024**3:.1f}/{self.data['memory'].total/1024**3:.1f} GB ({self.data['memory'].percent}%)\n"
            f"Swap: {self.data['swap'].used/1024**3:.1f}/{self.data['swap'].total/1024**3:.1f} GB```",
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
            f"RAM: {data['memory'].percent}%\n"
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