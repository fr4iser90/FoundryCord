from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import AuditLogEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.shared.domain.repositories.audit.audit_log_repository import AuditLogRepository

class AuditLogRepositoryImpl(BaseRepositoryImpl[AuditLogEntity], AuditLogRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLogEntity, session)
    
    async def get_by_id(self, log_id: int) -> Optional[AuditLogEntity]:
        result = await self.session.execute(select(AuditLogEntity).where(AuditLogEntity.id == log_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[AuditLogEntity]:
        result = await self.session.execute(
            select(AuditLogEntity)
            .where(AuditLogEntity.user_id == user_id)
            .order_by(AuditLogEntity.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_action(self, action: str, limit: int = 100) -> List[AuditLogEntity]:
        result = await self.session.execute(
            select(AuditLogEntity)
            .where(AuditLogEntity.action == action)
            .order_by(AuditLogEntity.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_logs(self, limit: int = 100) -> List[AuditLogEntity]:
        result = await self.session.execute(
            select(AuditLogEntity)
            .order_by(AuditLogEntity.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, user_id: str, action: str, details: Dict[str, Any]) -> AuditLogEntity:
        audit_log = AuditLogEntity(
            user_id=user_id,
            action=action,
            details=details
        )
        self.session.add(audit_log)
        await self.session.flush()
        await self.session.refresh(audit_log)
        return audit_log
    
    async def delete_older_than(self, days: int) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(AuditLogEntity).where(AuditLogEntity.timestamp < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        count = len(old_logs)
        for log in old_logs:
            await super().delete(log)
        
        return count