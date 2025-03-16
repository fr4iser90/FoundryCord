from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.models import LogEntry
from typing import Optional, List
from datetime import datetime, timedelta

class LogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, log_entry: LogEntry) -> LogEntry:
        """Add a new log entry to the database"""
        self.session.add(log_entry)
        await self.session.commit()
        return log_entry
    
    async def get_by_id(self, log_id: int) -> Optional[LogEntry]:
        """Get a log entry by ID"""
        result = await self.session.execute(select(LogEntry).where(LogEntry.id == log_id))
        return result.scalar_one_or_none()
    
    async def get_recent(self, limit: int = 100) -> List[LogEntry]:
        """Get recent log entries"""
        result = await self.session.execute(
            select(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit)
        )
        return result.scalars().all()
    
    async def delete_older_than(self, days: int = 30) -> int:
        """Delete log entries older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(LogEntry).where(LogEntry.timestamp < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        count = len(old_logs)
        for log in old_logs:
            await self.session.delete(log)
        
        await self.session.commit()
        return count
