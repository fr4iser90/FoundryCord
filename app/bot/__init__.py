"""
Homelab Discord Bot - Ein Discord-Bot zur Verwaltung und Überwachung von Homelab-Systemen.
"""

__version__ = "0.0.1"

# Einfachere Importe für häufig verwendete Klassen oder Funktionen
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
# from app.bot.infrastructure.factories import BotComponentFactory
# from app.bot.core.main import run_bot  # Falls du eine zentrale Startfunktion hast

import logging
logger = logging.getLogger("homelab.init")
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory

# Make these available globally for debugging
debug_component_registry = ComponentRegistry()
debug_component_factory = ComponentFactory(debug_component_registry)

logger.info("Created debug component registry and factory")
