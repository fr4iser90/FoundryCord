# app/bot/core/utilities/vars.py
import os
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()

# ===== SYSTEM-STATUS-TASK KONFIGURATION =====
# Zeitintervalle (in Sekunden)
UPDATE_INTERVAL_SHORT = 300      # 5 Minuten für schnelle Updates
UPDATE_INTERVAL_MEDIUM = 900     # 15 Minuten für ausgewogene Updates
UPDATE_INTERVAL_LONG = 1800      # 30 Minuten für ressourcenschonende Updates

# Standardwert aus Umgebungsvariable oder Fallback
DEFAULT_UPDATE_INTERVAL = int(os.getenv('STATUS_UPDATE_INTERVAL', UPDATE_INTERVAL_MEDIUM))

# Retry-Konfiguration für fehlgeschlagene Updates
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 10  # Sekunden

# ===== SCHWELLENWERTE FÜR SYSTEMWARNUNGEN =====
CPU_WARNING_THRESHOLD = 80       # Prozent
CPU_CRITICAL_THRESHOLD = 95      # Prozent
MEMORY_WARNING_THRESHOLD = 85    # Prozent
MEMORY_CRITICAL_THRESHOLD = 95   # Prozent
DISK_WARNING_THRESHOLD = 90      # Prozent
DISK_CRITICAL_THRESHOLD = 95     # Prozent

# ===== NETZWERK-KONFIGURATION =====
# Zu überwachende Netzwerkschnittstellen (erste gefundene wird verwendet)
NETWORK_INTERFACES = ["eth0", "ens33", "wlan0", "enp0s3"]
NETWORK_SPEED_UNITS = ["B/s", "KB/s", "MB/s", "GB/s"]
NETWORK_HISTORY_SIZE = 5  # Anzahl der zu speichernden Messungen für Durchschnittsberechnung

# ===== DOCKER-KONFIGURATION =====
DOCKER_ENABLED = os.getenv('DOCKER_ENABLED', 'true').lower() == 'true'
DOCKER_IMPORTANT_CONTAINERS = [
    "nginx", 
    "discord-server-bot", 
    "database", 
    "portainer", 
    "grafana"
]
DOCKER_MAX_CONTAINERS_TO_SHOW = 10  # Maximale Anzahl anzuzeigender Container

# ===== DIENSTE-KONFIGURATION =====
# Lokale Dienste (Port-basiert)
IMPORTANT_SERVICES = [
    {"name": "🔐 SSH", "port": 22},
    {"name": "🌐 Web", "port": 80},
    {"name": "🔒 HTTPS", "port": 443},
    {"name": "📊 Metrics", "port": 9090}
]

# Externe Dienste (URL-basiert)
DOMAIN = os.getenv('DOMAIN', 'example.com')
EXTERNAL_SERVICES = [
    {"name": "☁️ Cloud", "url_suffix": "cloud"},
    {"name": "📊 Grafana", "url_suffix": "grafana"},
    {"name": "🔄 Portainer", "url_suffix": "portainer"},
    {"name": "📁 Fileserver", "url_suffix": "files"},
    {"name": "📝 Nextcloud", "url_suffix": "nextcloud"}
]

# Timeout für externe Dienste-Anfragen
SERVICE_REQUEST_TIMEOUT = 5  # Sekunden

# ===== UI-KONFIGURATION =====
# Farben für Embeds
EMBED_COLOR_NORMAL = 0x7289da    # Discord Blau
EMBED_COLOR_WARNING = 0xffa500   # Orange
EMBED_COLOR_CRITICAL = 0xff0000  # Rot

# Fortschrittsbalken-Konfiguration
PROGRESS_BAR_LENGTH = 10
PROGRESS_BAR_FILLED = "█"
PROGRESS_BAR_EMPTY = "░"

# ===== SICHERHEITS-KONFIGURATION =====
# SSH-Sicherheit
SSH_LOG_PATH = "/var/log/auth.log"  # Pfad zur SSH-Log-Datei
SSH_LOG_FALLBACK_PATHS = [
    "/var/log/secure",
    "/var/log/sshd.log"
]
SSH_LOG_MAX_LINES = 1000  # Maximale Anzahl zu lesender Zeilen

# Firewall-Status
FIREWALL_CHECK_COMMAND = "ufw status | grep -q 'Status: active'"
FIREWALL_FALLBACK_COMMANDS = [
    "iptables -L | grep -q 'Chain INPUT'",
    "firewall-cmd --state | grep -q 'running'"
]

# ===== LOGGING-KONFIGURATION =====
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ===== SYSTEM-KONFIGURATION =====
# Pfade für Systemdateien
PROC_UPTIME_PATH = "/proc/uptime"
PROC_LOADAVG_PATH = "/proc/loadavg"
PROC_MEMINFO_PATH = "/proc/meminfo"
PROC_CPUINFO_PATH = "/proc/cpuinfo"

# CPU-Temperatur-Pfade (in Prioritätsreihenfolge)
CPU_TEMP_PATHS = [
    "/sys/class/thermal/thermal_zone0/temp",
    "/sys/devices/platform/coretemp.0/temp1_input",
    "/sys/bus/acpi/devices/LNXTHERM:00/thermal_zone/temp"
]

# ===== THREAD-KONFIGURATION =====
# Thread-Namen
PUBLIC_THREAD_NAME = "Public Status"
ADMIN_THREAD_NAME = "Admin Status"

# Thread-Archivierungszeit (in Minuten)
THREAD_ARCHIVE_DURATION = 1440  # 24 Stunden

# ===== FEATURE-FLAGS =====
# Aktivieren/Deaktivieren von Features
ENABLE_DOCKER_MONITORING = DOCKER_ENABLED
ENABLE_SSH_MONITORING = True
ENABLE_NETWORK_MONITORING = True
ENABLE_DISK_MONITORING = True
ENABLE_SERVICE_MONITORING = True
ENABLE_TEMPERATURE_MONITORING = True