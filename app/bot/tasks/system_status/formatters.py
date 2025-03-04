def progress_bar(percent):
    """Erstellt einen Text-basierten Fortschrittsbalken"""
    bars = "█" * int(percent/10) + "░" * (10 - int(percent/10))
    return f"{bars} {percent:.1f}%"

def get_system_color(cpu, memory, disk):
    """Bestimmt die Embed-Farbe basierend auf Auslastung"""
    if cpu > 80 or memory > 90 or disk > 90:
        return 0xff0000  # Rot 
    elif cpu > 60 or memory > 75 or disk > 75:
        return 0xffa500  # Orange
    return 0x00ff00      # Grün

def format_services_text(services):
    """Formatiert den Dienste-Status als Text"""
    if not services:
        return "Keine Dienste verfügbar"
    
    # Sortiere Dienste: Online zuerst, dann Geschützt, dann Timeout, dann Offline
    sorted_services = sorted(
        services.items(),
        key=lambda x: (0 if "✅" in x[1] else 
                      (1 if "🔒" in x[1] else 
                       (2 if "⏱️" in x[1] else 3)))
    )
    
    return "\n".join([f"{name}: {status}" for name, status in sorted_services])