import os
import platform
import subprocess
import logging

logger = logging.getLogger('homelab_bot')

async def get_ssh_attempts():
    """Ermittelt fehlgeschlagene SSH-Anmeldeversuche."""
    try:
        if platform.system() != "Linux":
            return "N/A (nur Linux)", "N/A"
        
        log_files = [
            "/var/log/auth.log",       # Debian/Ubuntu
            "/var/log/secure",         # RHEL/CentOS
            "/var/log/audit/audit.log" # Einige Systeme
        ]
        
        log_file = next((f for f in log_files if os.path.exists(f)), None)
        
        if not log_file:
            return "Log nicht gefunden", "N/A"
        
        cmd = f"grep 'Failed password' {log_file} | wc -l"
        attempts = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        
        # Use raw string for the regex pattern to avoid invalid escape sequence warning
        ip_cmd = f"grep 'Failed password' {log_file} | tail -1 | grep -oE r'([0-9]{{1,3}}\.?){{4}}'"
        try:
            last_ip = subprocess.check_output(ip_cmd, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            last_ip = "Keine"
        
        return attempts, last_ip
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der SSH-Versuche: {e}")
        return "N/A", "N/A"