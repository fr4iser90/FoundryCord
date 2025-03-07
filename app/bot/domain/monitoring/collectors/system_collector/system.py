import platform
import psutil
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('homelab_bot')

async def get_system_uptime():
    """Ermittelt die Systemlaufzeit."""
    try:
        if platform.system() == "Linux":
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
        else:
            uptime_seconds = time.time() - psutil.boot_time()
        
        uptime_time = timedelta(seconds=uptime_seconds)
        days = uptime_time.days
        hours, remainder = divmod(uptime_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} Tage, {hours} Stunden, {minutes} Minuten"
        else:
            return f"{hours} Stunden, {minutes} Minuten"
    
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln der Uptime: {e}")
        return "Unbekannt"

async def get_cpu_temperature():
    """Ermittelt die CPU-Temperatur, falls verfügbar."""
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:  # Für Raspberry Pi
                temp = temps['cpu_thermal'][0].current
            else:
                for sensor_name, sensor_readings in temps.items():
                    if sensor_readings:
                        temp = sensor_readings[0].current
                        break
                else:
                    return "N/A"
            return temp
        else:
            return "N/A"
    except Exception as e:
        logger.error(f"Fehler bei der Temperaturmessung: {e}")
        return "N/A"