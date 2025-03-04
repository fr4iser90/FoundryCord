import nextcord
from datetime import datetime
from .formatters import progress_bar, get_system_color, format_services_text

def create_public_embed(data):
    """Erstellt das Public-Status-Embed mit grundlegenden Informationen"""
    public_embed = nextcord.Embed(
        title="🏠 HomeLab Status - Public",
        description=f"System läuft seit: {data['uptime']}",
        color=get_system_color(data['cpu'], data['memory'].percent, data['disk'].percent),
        timestamp=datetime.now()
    ).add_field(
        name="Dienste",
        value=format_services_text(data['services']),
        inline=False
    ).add_field(
        name="Auslastung",
        value=(
            "```diff\n"
            f"+ CPU:  {progress_bar(data['cpu'])}\n"
            f"+ RAM:  {progress_bar(data['memory'].percent)}\n"
            f"+ Disk: {progress_bar(data['disk'].percent)}\n"
            "```"
        ),
        inline=False
    ).add_field(
        name="Netzwerk",
        value=f"Aktuelle Geschwindigkeit: {data['net_public']}",
        inline=False
    ).set_footer(text=f"Aktualisiert | Domain: {data['domain']}")
    
    return public_embed