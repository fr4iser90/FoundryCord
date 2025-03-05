"""Check web services via HTTP/HTTPS"""
import asyncio
import aiohttp
import logging

logger = logging.getLogger('homelab_bot')

async def check_web_services(services_list):
    """Check HTTP/HTTPS web services"""
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for service in services_list:
            try:
                async with session.get(service["url"], timeout=5, ssl=False) as response:
                    if response.status < 400:
                        results[service["name"]] = "✅ Online"
                    elif response.status in [401, 403]:
                        results[service["name"]] = "🔒 Geschützt"
                    else:
                        results[service["name"]] = f"❌ Status {response.status}"
            except asyncio.TimeoutError:
                results[service["name"]] = "⏱️ Timeout"
            except Exception as e:
                logger.debug(f"Fehler bei {service['name']}: {str(e)}")
                results[service["name"]] = "❌ Offline"
    
    return results