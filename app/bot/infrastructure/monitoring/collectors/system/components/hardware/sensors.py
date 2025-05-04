import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger('homelab_bot')

async def get_sensor_info() -> Dict[str, Any]:
    """Sammelt Sensor-Informationen (Temperaturen, Lüfter etc.)"""
    try:
        sensors = {}
        
        # CPU Temperaturen
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        sensors[f'temp_{name}_{entry.label or "cpu"}'] = entry.current
        except:
            sensors['cpu_temp'] = "N/A"
            
        # Lüfter-Geschwindigkeiten
        try:
            fans = psutil.sensors_fans()
            if fans:
                for name, entries in fans.items():
                    for i, entry in enumerate(entries):
                        sensors[f'fan_{name}_{i}'] = entry.current
        except:
            sensors['fans'] = "N/A"
            
        return sensors
    except Exception as e:
        logger.error(f"Sensor info error: {e}", exc_info=True)
        return {
            'sensors': "Nicht verfügbar",
            'error': str(e)
        }