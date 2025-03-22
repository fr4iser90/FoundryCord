from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.models import AuditLog
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.shared.domain.repositories.audit.audit_log_repository import AuditLogRepository

class AuditLogRepositoryImpl(AuditLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        result = await self.session.execute(select(AuditLog).where(AuditLog.id == log_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, user_id: str, action: str, details: Dict[str, Any]) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details
        )
        self.session.add(audit_log)
        await self.session.commit()
        return audit_log
    
    async def delete_older_than(self, days: int) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(AuditLog).where(AuditLog.timestamp < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        count = len(old_logs)
        for log in old_logs:
            await self.session.delete(log)
        
        await self.session.commit()
        return count