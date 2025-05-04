import psutil
import logging
import os
from typing import Dict, Any
import subprocess

logger = logging.getLogger('homelab_bot')

def read_sysfs_file(path: str) -> str:
    """Liest eine Datei aus dem sysfs"""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.debug(f"Konnte {path} nicht lesen: {e}")
        return None

async def get_power_info() -> Dict[str, Any]:
    """Sammelt Stromverbrauch-Informationen"""
    try:
        power_info = {}
        power_status = []
        
        # Batterie-Information
        try:
            battery = psutil.sensors_battery()
            if battery:
                power_info['battery_percent'] = f"{battery.percent}%"
                power_info['battery_status'] = "Am Netz" if battery.power_plugged else "Batteriebetrieb"
                if battery.secsleft != -1:
                    minutes = battery.secsleft // 60
                    power_info['battery_remaining'] = f"{minutes} Minuten"
                power_status.append(f"Batterie: {power_info['battery_percent']} ({power_info['battery_status']})")
        except Exception as e:
            logger.debug(f"Keine Batterie gefunden: {e}")

        # CPU Power
        try:
            rapl_paths = [
                '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj',
                '/sys/class/powercap/amd_energy/energy_uj'
            ]
            for path in rapl_paths:
                if os.path.exists(path):
                    energy = read_sysfs_file(path)
                    if energy:
                        power_info['cpu_power'] = f"{float(energy) / 1_000_000:.2f}W"
                        power_status.append(f"CPU Verbrauch: {power_info['cpu_power']}")
                        break
        except Exception as e:
            logger.debug(f"Kein CPU Power-Monitoring verfügbar: {e}")

        # PSU Status
        try:
            psu_path = '/sys/class/power_supply'
            if os.path.exists(psu_path):
                for psu in os.listdir(psu_path):
                    psu_full_path = os.path.join(psu_path, psu)
                    type_path = os.path.join(psu_full_path, 'type')
                    if os.path.exists(type_path) and read_sysfs_file(type_path) == 'Mains':
                        online_path = os.path.join(psu_full_path, 'online')
                        if os.path.exists(online_path):
                            status = "Online" if read_sysfs_file(online_path) == '1' else "Offline"
                            power_info['psu_status'] = status
                            power_status.append(f"Netzteil: {status}")
        except Exception as e:
            logger.debug(f"Kein PSU-Status verfügbar: {e}")

        # Finale Power-Status Zusammenfassung
        if power_status:
            power_info['power_status'] = '\n'.join(power_status)
        else:
            power_info['power_status'] = "System läuft, keine detaillierten Power-Informationen verfügbar"
            
        return power_info

    except Exception as e:
        logger.error(f"Error collecting power information: {e}", exc_info=True)
        return {
            'power_status': "Fehler beim Abrufen der Power-Informationen"
        }