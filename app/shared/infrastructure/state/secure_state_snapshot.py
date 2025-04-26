"""
Secure State Snapshot - Provides secure mechanisms for capturing state information
from browser or runtime environments with user approval.
"""
from typing import Dict, Any, Optional, List, Callable, Union
import json
import hashlib
import time
import logging
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

class SecureStateSnapshot:
    """
    Provides mechanisms for securely capturing targeted state information
    from browser or runtime environments with explicit user approval.
    """
    
    def __init__(self):
        self.registered_collectors = {}
        self.approved_collectors = set()
        self.pending_approvals = {}
        self.snapshot_history = {}
        
    def register_collector(self, name: str, collector_fn: Callable, 
                           requires_approval: bool = True,
                           scope: str = "global",
                           description: str = None):
        """
        Register a state collector function
        
        Args:
            name: Unique identifier for the collector
            collector_fn: Function that captures state information
            requires_approval: Whether explicit user approval is needed
            scope: The scope of this collector (bot, web, global)
            description: Human-readable description of what this collector captures
        """
        if name in self.registered_collectors:
            logger.warning(f"Overwriting existing state collector: {name}")
            
        self.registered_collectors[name] = {
            "function": collector_fn,
            "requires_approval": requires_approval,
            "scope": scope,
            "description": description or f"State collector for {name}",
            "registered_at": time.time()
        }
        logger.info(f"Registered state collector: {name} (scope: {scope})")
        
    def approve_collector(self, name: str, user_id: str = None) -> bool:
        """
        Approve a state collector for use
        
        Args:
            name: Name of the collector to approve
            user_id: ID of user providing approval
            
        Returns:
            bool: Whether the approval was successful
        """
        if name not in self.registered_collectors:
            logger.warning(f"Cannot approve unknown collector: {name}")
            return False
            
        if not self.registered_collectors[name]["requires_approval"]:
            logger.debug(f"Collector {name} doesn't require approval")
            return True
            
        # Add to approved collectors with user attribution
        approval_entry = {
            "approved_at": time.time(),
            "approved_by": user_id
        }
        
        self.approved_collectors.add(name)
        self.pending_approvals[name] = approval_entry
        logger.info(f"Approved state collector: {name} by user {user_id}")
        return True
        
    async def collect_state(self, collector_names: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect state using the specified collectors
        
        Args:
            collector_names: List of collector names to execute
            context: Optional context data to pass to collectors
            
        Returns:
            Dict containing collected state information
        """
        results = {}
        context = context or {}
        timestamp = time.time()
        
        for name in collector_names:
            if name not in self.registered_collectors:
                logger.warning(f"Unknown state collector: {name}")
                continue
                
            collector = self.registered_collectors[name]
            
            # Check if approval is required but not granted
            if collector["requires_approval"] and name not in self.approved_collectors:
                logger.warning(f"Cannot use unapproved collector: {name}")
                results[name] = {"error": "not_approved", "requires_approval": True}
                continue
                
            try:
                collector_fn = collector["function"]
                if callable(collector_fn):
                    result = await collector_fn(context) if hasattr(collector_fn, "__await__") else collector_fn(context)
                    results[name] = result
                    
                    # Store in history
                    if name not in self.snapshot_history:
                        self.snapshot_history[name] = []
                    self.snapshot_history[name].append({
                        "timestamp": timestamp,
                        "data": result
                    })
                    
                    logger.debug(f"Successfully collected state with: {name}")
                else:
                    logger.error(f"Collector {name} is not callable")
                    results[name] = {"error": "not_callable"}
            except Exception as e:
                logger.error(f"Error executing state collector {name}: {str(e)}")
                results[name] = {"error": str(e)}
                
        return {
            "timestamp": timestamp,
            "results": results
        }
        
    def get_available_collectors(self, scope: str = None) -> List[Dict[str, Any]]:
        """
        Get information about available collectors
        
        Args:
            scope: Optional scope filter (bot, web, global)
            
        Returns:
            List of collector information dictionaries
        """
        collectors = []
        
        for name, info in self.registered_collectors.items():
            if scope and info["scope"] != scope and info["scope"] != "global":
                continue
                
            collectors.append({
                "name": name,
                "description": info["description"],
                "requires_approval": info["requires_approval"],
                "scope": info["scope"],
                "is_approved": name in self.approved_collectors
            })
            
        return collectors

# Singleton instance
_state_snapshot_service = SecureStateSnapshot()

def get_state_snapshot_service() -> SecureStateSnapshot:
    """Get the global state snapshot service instance"""
    return _state_snapshot_service

# --- Register Default Server-Side Collectors --- 

# Importiere den Service
_service_instance = get_state_snapshot_service()

# Beispiel-Collector für Bot-Info
def get_bot_status_info(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("Executing bot_status state collector...")
    # TODO: Replace with actual bot interaction or cached data
    try:
        # Beispiel: Versuche, Daten von einer (noch nicht existierenden) Bot-Verwaltung zu holen
        # from app.bot.manager import get_bot_manager 
        # bot_manager = get_bot_manager()
        # status = bot_manager.get_status()
        # return status 
        return {
            "status": "online_placeholder",
            "uptime_seconds": 12345,
            "guild_count": 5,
            "command_prefix": "!",
            "latency_ms": 50
        }
    except Exception as e:
        logger.error(f"Error in bot_status collector: {e}", exc_info=True)
        return {"error": str(e)}

_service_instance.register_collector(
    name="bot_status",
    collector_fn=get_bot_status_info,
    requires_approval=False, 
    scope="bot",
    description="Basic status information about the Discord bot (Placeholder)"
)

# Beispiel-Collector für System-Info
import platform
import os

def get_system_info(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("Executing system_info state collector...")
    try:
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "cpu_cores": os.cpu_count()
            # Avoid adding overly sensitive information here
        }
    except Exception as e:
        logger.error(f"Error in system_info collector: {e}", exc_info=True)
        return {"error": str(e)}

_service_instance.register_collector(
    name="system_info",
    collector_fn=get_system_info,
    requires_approval=False,
    scope="web", 
    description="Basic OS and Python environment details"
)

# Fügen Sie hier weitere Server-Collectors hinzu... 