import psutil
import logging
import os

logger = logging.getLogger('homelab_bot')

async def get_disk_usage_all():
    """Ermittelt die Festplattennutzung aller relevanten Laufwerke."""
    try:
        partitions = psutil.disk_partitions(all=False)  # Nur echte Festplatten
        result = "```\n"
        
        # Pfade die übersprungen werden sollen
        skip_paths = {
            '/etc', '/proc', '/sys', '/dev', '/run', '/docker',
            '/snap', '/boot', '/var/lib/docker', '/var/snap',
            '/app/bot/database'  # Füge Docker-Volume-Pfade hinzu
        }
        
        # Pfade die bereits verarbeitet wurden
        processed_mounts = set()
        
        for partition in partitions:
            # Überspringe spezielle Dateisysteme und temporäre Dateisysteme
            if (any(partition.mountpoint.startswith(skip) for skip in skip_paths) or
                partition.fstype in ('tmpfs', 'devtmpfs', 'devpts', 'squashfs', 'overlay')):
                continue
                
            # Überspringe, wenn der Mountpoint bereits verarbeitet wurde
            if partition.mountpoint in processed_mounts:
                continue
                
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                # Nur Laufwerke mit mehr als 1GB anzeigen
                if usage.total >= (1024**3):  # 1 GB
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    # Formatiere die Ausgabe
                    result += f"{partition.mountpoint} ({partition.fstype}): "
                    result += f"{used_gb:.1f}/{total_gb:.1f} GB ({usage.percent}%)\n"
                    processed_mounts.add(partition.mountpoint)
            except (PermissionError, OSError):
                continue
        
        # Wenn keine Laufwerke gefunden wurden
        if len(processed_mounts) == 0:
            return "Keine Festplatten gefunden"
            
        result += "```"
        return result
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Festplattennutzung: {e}")
        return "Festplattennutzung nicht verfügbar"