import json
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import os

logger = logging.getLogger('homelab_bot')

class CollectorCache:
    """Centralized cache service for all collectors to prevent excessive resource usage"""
    
    _instance = None
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_file = "/tmp/homelab_collector_cache.json"
    _default_ttl = timedelta(minutes=10)  # Default cache expiry
    _ttl_config = {
        # Customize TTLs for different collector types
        "speedtest": timedelta(hours=24),
        "ssh_attempts": timedelta(hours=1),
        "service_status": timedelta(minutes=5),
        "docker_status": timedelta(minutes=5),
        "system_metrics": timedelta(minutes=2),
    }
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CollectorCache, cls).__new__(cls)
            cls._instance._load_cache()
        return cls._instance
    
    def _load_cache(self):
        """Load cache from file if it exists"""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, "r") as f:
                    file_data = json.load(f)
                    
                    # Convert ISO strings back to datetime objects
                    for collector_id, entry in file_data.items():
                        if "timestamp" in entry:
                            entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
                    
                    self._cache = file_data
                    logger.debug(f"Loaded cache with {len(self._cache)} entries")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self._cache = {}
    
    async def _save_cache(self):
        """Save cache to file"""
        try:
            async with self._lock:
                # Prepare data for serialization (convert datetime to ISO format)
                serializable_cache = {}
                for collector_id, entry in self._cache.items():
                    serializable_cache[collector_id] = entry.copy()
                    if "timestamp" in entry and isinstance(entry["timestamp"], datetime):
                        serializable_cache[collector_id]["timestamp"] = entry["timestamp"].isoformat()
                
                with open(self._cache_file, "w") as f:
                    json.dump(serializable_cache, f)
                logger.debug(f"Saved cache with {len(self._cache)} entries")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def get(self, collector_id: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get cached data if it exists and is not expired
        
        Args:
            collector_id: The collector identifier
            force_refresh: If True, ignore cache and return None to force data collection
        """
        if force_refresh:
            logger.debug(f"Force refresh requested for {collector_id}, ignoring cache")
            return None
            
        if collector_id not in self._cache:
            return None
            
        entry = self._cache[collector_id]
        ttl = self._get_ttl(collector_id)
        
        # Check if cache is expired
        if "timestamp" in entry and datetime.now() - entry["timestamp"] < ttl:
            logger.debug(f"Cache hit for {collector_id}, age: {datetime.now() - entry['timestamp']}")
            return entry.get("data")
        
        logger.debug(f"Cache expired for {collector_id}")
        return None
    
    async def set(self, collector_id: str, data: Any) -> None:
        """Store data in cache"""
        async with self._lock:
            self._cache[collector_id] = {
                "data": data,
                "timestamp": datetime.now()
            }
            await self._save_cache()
    
    def _get_ttl(self, collector_id: str) -> timedelta:
        """Get the appropriate TTL for this collector type"""
        # Extract collector type from ID (e.g., "speedtest_default" → "speedtest")
        collector_type = collector_id.split("_")[0]
        return self._ttl_config.get(collector_type, self._default_ttl)
    
    def is_running(self, collector_id: str) -> bool:
        """Check if a collector is currently running to prevent duplicate executions"""
        return collector_id in self._cache and self._cache[collector_id].get("running", False)
    
    async def set_running(self, collector_id: str, running: bool = True) -> None:
        """Mark a collector as running or not running"""
        async with self._lock:
            if collector_id in self._cache:
                self._cache[collector_id]["running"] = running
            else:
                self._cache[collector_id] = {"running": running, "timestamp": datetime.now()}
            await self._save_cache()
