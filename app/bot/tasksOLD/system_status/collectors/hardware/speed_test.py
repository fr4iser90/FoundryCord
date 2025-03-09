import aiohttp
import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import speedtest
from functools import partial

logger = logging.getLogger('homelab_bot')

class SpeedTestManager:
    def __init__(self, cache_file: str = "/tmp/speed_test_cache.json"):  # Changed path to /tmp for Docker
        self.cache_file = cache_file
        self.cache_duration = timedelta(hours=24)
        self._cached_results: Optional[Dict] = None
        self._last_test: Optional[datetime] = None
        self._is_testing = False  # Add lock to prevent multiple tests

    async def perform_speed_test(self) -> Dict[str, float]:
        """Führt einen vollständigen Speed Test durch"""
        if self._is_testing:
            logger.info("Speed test already in progress, returning cached or default values")
            return await self._load_results() or {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        try:
            self._is_testing = True
            logger.info("Starting speed test...")
            
            # Run speedtest in a thread pool to not block
            loop = asyncio.get_event_loop()
            st = await loop.run_in_executor(None, self._run_speedtest)
            
            results = {
                "download": st["download"] / 1_000_000,  # Convert to Mbps
                "upload": st["upload"] / 1_000_000,      # Convert to Mbps
                "ping": st["ping"],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Speed test completed: {results}")
            await self._save_results(results)
            return results
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
            return {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self._is_testing = False

    def _run_speedtest(self) -> Dict[str, float]:
        """Führt den eigentlichen Speedtest durch"""
        logger.info("Initializing speedtest...")
        st = speedtest.Speedtest()
        
        logger.info("Getting best server...")
        st.get_best_server()
        
        logger.info("Running download test...")
        download = st.download()
        
        logger.info("Running upload test...")
        upload = st.upload()
        
        logger.info("Getting ping...")
        ping = st.results.ping
        
        return {
            "download": download,
            "upload": upload,
            "ping": ping
        }

    async def get_speed_info(self) -> Dict[str, float]:
        """Holt Speed Test Ergebnisse (cached oder neu)"""
        cached = await self._load_results()
        if cached:
            return cached
        return await self.perform_speed_test()

    async def _test_download(self, session: aiohttp.ClientSession) -> float:
        try:
            start_time = datetime.now()
            async with session.get('https://speed.cloudflare.com/__down') as response:
                data = await response.read()
                duration = (datetime.now() - start_time).total_seconds()
                return (len(data) * 8 / 1_000_000) / duration  # Mbps
        except Exception as e:
            logger.error(f"Download test failed: {e}")
            return 0.0

    async def _test_upload(self, session: aiohttp.ClientSession) -> float:
        # Implement a proper upload test here
        # This is a simplified version
        return 0.0  # Placeholder

    async def _save_results(self, results: Dict) -> None:
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(results, f)
        except Exception as e:
            logger.error(f"Failed to cache speed test results: {e}")

    async def _load_results(self) -> Optional[Dict]:
        try:
            if not os.path.exists(self.cache_file):
                return None
                
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data['timestamp'])
                
                if datetime.now() - timestamp > self.cache_duration:
                    return None
                    
                return data
        except Exception as e:
            logger.error(f"Failed to load cached speed test results: {e}")
            return None