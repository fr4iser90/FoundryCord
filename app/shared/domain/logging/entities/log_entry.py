from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class LogEntry:
    """Domain entity representing a log entry"""
    message: str
    level: str
    logger_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "application"  # 'bot', 'web', 'db', etc.
    context: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None
    
    @property
    def is_error(self) -> bool:
        """Check if this log entry represents an error"""
        return self.level in ("ERROR", "CRITICAL")