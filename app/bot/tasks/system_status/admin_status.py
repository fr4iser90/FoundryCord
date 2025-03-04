import nextcord
from datetime import datetime

def create_admin_embed(data):
    """Erstellt das Admin-Status-Embed mit detaillierten Informationen"""
    admin_embed = nextcord.Embed(
        title="🔒 HomeLab Status - Admin",
        description=f"System: {data['platform']} {data['release']} | Uptime: {data['uptime']}",
        color=0x7289da,
        timestamp=datetime.now()
    ).add_field(
        name="Hardware",
        value=(
            f"CPU: {data['cpu']}% ({data['cpu_temp']}°C)\n"
            f"RAM: {data['memory'].used/1024**3:.1f}/{data['memory'].total/1024**3:.1f} GB ({data['memory'].percent}%)\n"
            f"Swap: {data['swap'].used/1024**3:.1f}/{data['swap'].total/1024**3:.1f} GB"
        ),
        inline=False
    ).add_field(
        name="Netzwerk",
        value=f"```\n{data['net_admin']}\n```",
        inline=False
    ).add_field(
        name="Festplatten",
        value=data['disk_details'],
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
    ).add_field(
        name="Docker Container",
        value=(
            "```ini\n"
            f"[Status]\n"
            f"Running: {data['docker_running']}\n"
            f"Errors: {data['docker_errors']}\n\n"
            f"[Container]\n{data['docker_details']}\n"
            "```"
        ),
        inline=False
    ).set_footer(text=f"Domain: {data['domain']} | IP: {data['public_ip']}")
    
    return admin_embed