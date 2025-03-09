"""Configuration for game-related services"""

def get_pufferpanel_services():
    return [
        {"name": "🎮 Minecraft", "port_range": (25565, 25575), "container": "pufferpanel", "protocol": "both"},
        {"name": "🎮 Factorio", "port_range": (34197, 34207), "container": "pufferpanel", "protocol": "both"}, 
        {"name": "🎮 CS2", "port_range": (27015, 27025), "container": "pufferpanel", "protocol": "both"},
        {"name": "🎮 Valheim", "port_range": (2456, 2466), "container": "pufferpanel", "protocol": "both"},
    ]

def get_standalone_services():
    return [
        {"name": "🎮 Palworld", "port_range": (8211, 8221), "container": "palworld-server", "protocol": "both"},
        {"name": "🎮 Satisfactory", "port_range": (7777, 7787), "container": "satisfactory-server", "protocol": "both"},
    ]