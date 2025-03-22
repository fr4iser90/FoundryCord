from fastapi import APIRouter, Depends, HTTPException, Request
from app.web.application.services.auth.dependencies import get_current_user
import psutil
from datetime import datetime, timedelta
import random  # Nur für Mock-Daten, später entfernen

# Router mit Präfix erstellen
router = APIRouter(prefix="/bot", tags=["Bot API"])

@router.get("/system-resources")
async def get_system_resources(current_user = Depends(get_current_user)):
    """
    Gibt aktuelle System-Ressourcen zurück (CPU, RAM)
    """
    return {
        "cpu": round(psutil.cpu_percent(), 1),
        "memory": round(psutil.virtual_memory().percent, 1),
        "memory_used": f"{psutil.virtual_memory().used / (1024*1024*1024):.1f}GB",
        "memory_total": f"{psutil.virtual_memory().total / (1024*1024*1024):.1f}GB"
    }

@router.get("/recent-activities")
async def get_recent_activities(current_user = Depends(get_current_user)):
    """
    Gibt die letzten Bot-Aktivitäten zurück
    In einer realen Implementierung würden diese aus der Datenbank geladen
    """
    # Mock-Daten für Entwicklungszwecke
    activity_types = ["command", "member_join", "member_leave", "message", "error", "warning", "info"]
    activities = []
    
    now = datetime.now()
    for i in range(10):
        activity_time = now - timedelta(minutes=random.randint(1, 120))
        activity_type = random.choice(activity_types)
        
        description = ""
        if activity_type == "command":
            commands = ["help", "ban", "kick", "mute", "info", "stats", "play", "skip"]
            description = f"User executed /{random.choice(commands)} command"
        elif activity_type == "member_join":
            description = "New member joined the server"
        elif activity_type == "member_leave":
            description = "Member left the server"
        elif activity_type == "message":
            description = "Message processed by bot"
        elif activity_type == "error":
            description = "Error occurred during command execution"
        elif activity_type == "warning":
            description = "Warning during permission check"
        elif activity_type == "info":
            description = "Bot configuration updated"
        
        activities.append({
            "type": activity_type,
            "icon": get_icon_for_activity(activity_type),
            "timestamp": activity_time.isoformat(),
            "description": description,
            "server": f"Server {random.randint(1, 5)}"
        })
    
    return sorted(activities, key=lambda x: x["timestamp"], reverse=True)

@router.get("/servers")
async def get_servers(current_user = Depends(get_current_user)):
    """
    Gibt Liste der Server zurück, auf denen der Bot aktiv ist
    In einer realen Implementierung würde dies aus der Datenbank kommen
    """
    # Mock-Daten
    server_names = ["Gaming Hub", "Dev Community", "Support Server", "HomeLab Discussions", "Meme Central"]
    servers = []
    
    for i in range(5):
        has_icon = random.choice([True, False])
        icon_url = f"https://placehold.co/100x100/7289da/ffffff?text={i+1}" if has_icon else None
        
        # Simulierte Berechtigungen
        permissions = {
            "admin": random.choice([True, False]),
            "manage_server": random.choice([True, False]),
            "manage_channels": random.choice([True, False])
        }
        
        servers.append({
            "id": f"server_{i+1}",
            "name": server_names[i] if i < len(server_names) else f"Server {i+1}",
            "icon_url": icon_url,
            "member_count": random.randint(10, 1000),
            "user_permissions": permissions
        })
    
    return servers

@router.get("/popular-commands")
async def get_popular_commands(current_user = Depends(get_current_user)):
    """
    Gibt die populärsten Bot-Befehle zurück
    """
    # Beispieldaten für populäre Befehle
    commands = [
        {"name": "help", "description": "Shows help information", "usage_count": random.randint(50, 200)},
        {"name": "info", "description": "Shows bot information", "usage_count": random.randint(30, 150)},
        {"name": "stats", "description": "Shows server statistics", "usage_count": random.randint(20, 100)},
        {"name": "play", "description": "Plays music from URL", "usage_count": random.randint(10, 80)},
        {"name": "ban", "description": "Bans a user", "usage_count": random.randint(5, 50)}
    ]
    
    # Nach Nutzungshäufigkeit absteigend sortieren
    commands.sort(key=lambda x: x["usage_count"], reverse=True)
    return commands

# Hilfsfunktion für passende Icons
def get_icon_for_activity(activity_type):
    icons = {
        "command": "terminal",
        "member_join": "person-plus",
        "member_leave": "person-dash",
        "message": "chat-text",
        "error": "exclamation-triangle",
        "warning": "exclamation-circle",
        "info": "info-circle"
    }
    return icons.get(activity_type, "question-circle")