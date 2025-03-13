"""Main service status collection module"""
import logging
import asyncio

from app.bot.infrastructure.monitoring.collectors.service.config.game_services import get_pufferpanel_services, get_standalone_services
from app.bot.infrastructure.monitoring.collectors.service.config.web_services import get_public_services, get_private_services
from app.bot.infrastructure.monitoring.checkers.game_service_checker import check_pufferpanel_games, check_standalone_games
from app.bot.infrastructure.monitoring.checkers.web_service_checker import check_web_services
from app.shared.logging import logger

async def check_services_status(include_private=False):
    """Überprüft den Status wichtiger Dienste."""
    try:
        # Get service configurations
        pufferpanel_services = get_pufferpanel_services()
        standalone_services = get_standalone_services()
        public_services = get_public_services()
        private_services = get_private_services() if include_private else []
        
        # Run checks sequentially like in original code (to avoid potential hanging)
        results = {}
        
        # Game server checks with timeouts
        try:
            pufferpanel_results = await asyncio.wait_for(
                check_pufferpanel_games(pufferpanel_services), 
                timeout=5.0  # Shorter timeout like your original
            )
            results.update(pufferpanel_results)
        except asyncio.TimeoutError:
            logger.warning("Timeout checking pufferpanel games")
            for service in pufferpanel_services:
                results[service["name"]] = "⏱️ Timeout"
        except Exception as e:
            logger.warning(f"Error checking pufferpanel games: {e}")
        
        try:
            standalone_results = await asyncio.wait_for(
                check_standalone_games(standalone_services),
                timeout=5.0
            )
            results.update(standalone_results)
        except asyncio.TimeoutError:
            logger.warning("Timeout checking standalone games")
            for service in standalone_services:
                results[service["name"]] = "⏱️ Timeout"
        except Exception as e:
            logger.warning(f"Error checking standalone games: {e}")
        
        # Web service checks
        try:
            web_results = await asyncio.wait_for(
                check_web_services(public_services + private_services),
                timeout=5.0
            )
            results.update(web_results)
        except asyncio.TimeoutError:
            logger.warning("Timeout checking web services")
            for service in public_services + private_services:
                results[service["name"]] = "⏱️ Timeout"
        except Exception as e:
            logger.warning(f"Error checking web services: {e}")
        
        return results
        
    except Exception as e:
        logger.debug(f"Fehler bei check_services_status: {str(e)}")
        return {"error": "⚠️ Fehler beim Überprüfen der Dienste"}
