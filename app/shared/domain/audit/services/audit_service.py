from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from app.shared.domain.audit.entities.audit_record import AuditRecord

class AuditService(ABC):
    """Domain service for tracking business-relevant auditable actions"""
    
    @abstractmethod
    def record_action(self, action: str, actor_id: str, entity_id: Optional[str] = None, 
                      details: Optional[dict] = None) -> None:
        """Record a business action for audit purposes"""
        pass
    
    @abstractmethod
    def get_actions_by_user(self, user_id: str, from_date: Optional[datetime] = None,
                           to_date: Optional[datetime] = None) -> list[AuditRecord]:
        """Retrieve actions performed by a specific user"""
        pass
    
    # Weitere Audit-bezogene Methoden... 