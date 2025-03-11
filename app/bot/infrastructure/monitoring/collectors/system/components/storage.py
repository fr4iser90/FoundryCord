import psutil
import logging
import os

logger = logging.getLogger('homelab_bot')

async def get_disk_usage_all():
    """Ermittelt die Festplattennutzung aller relevanten Laufwerke."""
    try:
        partitions = psutil.disk_partitions(all=False)  # Nur echte Festplatten
        result_dict = {}
        
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
                    # Speichere Daten im Dictionary statt als Text
                    result_dict[partition.mountpoint] = {
                        "used": usage.used,
                        "total": usage.total,
                        "percent": usage.percent,
                        "fstype": partition.fstype
                    }
                    processed_mounts.add(partition.mountpoint)
            except (PermissionError, OSError):
                continue
        
        # Wenn keine Laufwerke gefunden wurden
        if len(processed_mounts) == 0:
            return {}  # Leeres Dictionary bei Fehler
            
        return result_dict
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Festplattennutzung: {e}")
        return {}  # Leeres Dictionary bei Fehler