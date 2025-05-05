"""
Homelab Discord Bot - Ein Discord-Bot zur Verwaltung und Überwachung von Homelab-Systemen.
"""

__version__ = "0.0.1"

# Einfachere Importe für häufig verwendete Klassen oder Funktionen
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
# from app.bot.infrastructure.factories import BotComponentFactory
# from app.bot.core.main import run_bot  # Falls du eine zentrale Startfunktion hast
# from .config import SHARED_CONFIG_VALUE
