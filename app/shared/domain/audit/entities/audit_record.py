from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class AuditRecord:
    """Domain entity representing an audit record of a business action"""
    action: str               # z.B. "ROLE_ASSIGNED", "CHANNEL_CREATED"
    actor_id: str             # Wer hat die Aktion ausgeführt
    timestamp: datetime = field(default_factory=datetime.now)
    entity_id: Optional[str] = None  # Auf welche Entität bezieht sich die Aktion
    entity_type: Optional[str] = None  # Art der Entität (z.B. "USER", "CHANNEL")
    details: Dict[str, Any] = field(default_factory=dict)  # Weitere Informationen
    
    @property
    def is_sensitive(self) -> bool:
        """Check if this audit record contains sensitive information"""
        return self.action in ("PASSWORD_CHANGED", "ROLE_CHANGED", "PERMISSION_GRANTED") 