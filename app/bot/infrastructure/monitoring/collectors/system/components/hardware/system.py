import platform
import logging
from typing import Dict, Any
import psutil
from datetime import datetime
import json

logger = logging.getLogger('homelab_bot')

async def get_system_info() -> Dict[str, Any]:
    """Sammelt System-spezifische Informationen"""
    try:
        # Versuche den echten Hostnamen in verschiedenen Quellen zu finden
        real_hostname = None
        
        # 1. Versuche /etc/hostname
        try:
            with open('/etc/hostname', 'r') as f:
                real_hostname = f.read().strip()
                logger.debug(f"Hostname aus /etc/hostname gelesen: {real_hostname}")
        except Exception as e:
            logger.debug(f"Konnte /etc/hostname nicht lesen: {e}")

        # 2. Versuche NixOS config wenn noch kein Hostname gefunden
        if not real_hostname:
            try:
                with open('/etc/nixos/system-config.nix', 'r') as f:
                    config_content = f.read()
                    # Suche nach hostName = "Name";
                    import re
                    hostname_match = re.search(r'hostName\s*=\s*"([^"]+)"', config_content)
                    if hostname_match:
                        real_hostname = hostname_match.group(1)
                        logger.debug(f"Hostname aus NixOS config gelesen: {real_hostname}")
            except Exception as e:
                logger.debug(f"Konnte NixOS config nicht lesen: {e}")

        # 3. Fallback auf platform.node() wenn immer noch kein Hostname
        if not real_hostname:
            real_hostname = platform.node()
            logger.debug(f"Fallback auf platform.node(): {real_hostname}")
            
        return {
            'system_platform': platform.platform(),
            'system_release': platform.release(),
            'system_version': platform.version(),
            'system_machine': platform.machine(),
            'system_processor': platform.processor(),
            'system_uptime': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'system_hostname': real_hostname
        }
    except Exception as e:
        logger.error(f"System Info Fehler: {e}")
        return {
            'system_platform': "N/A",
            'system_version': "N/A",
            'system_hostname': "Unbekannt"
        }