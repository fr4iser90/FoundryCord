from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Session
from typing import Optional, List
from datetime import datetime

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, session_id: int) -> Optional[Session]:
        result = await self.session.execute(select(Session).where(Session.id == session_id))
        return result.scalar_one_or_none()
    
    async def get_by_token(self, token: str) -> Optional[Session]:
        result = await self.session.execute(select(Session).where(Session.token == token))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> List[Session]:
        result = await self.session.execute(select(Session).where(Session.user_id == user_id))
        return result.scalars().all()
    
    async def get_active_sessions(self) -> List[Session]:
        now = datetime.utcnow()
        result = await self.session.execute(select(Session).where(Session.expires_at > now))
        return result.scalars().all()
    
    async def create(self, user_id: str, token: str, expires_at: datetime) -> Session:
        session_obj = Session(user_id=user_id, token=token, expires_at=expires_at)
        self.session.add(session_obj)
        await self.session.commit()
        return session_obj
    
    async def update(self, session_obj: Session) -> Session:
        self.session.add(session_obj)
        await self.session.commit()
        return session_obj
    
    async def delete(self, session_obj: Session) -> None:
        await self.session.delete(session_obj)
        await self.session.commit()
    
    async def delete_expired(self) -> int:
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Session).where(Session.expires_at <= now)
        )
        expired_sessions = result.scalars().all()
        
        count = len(expired_sessions)
        for session_obj in expired_sessions:
            await self.session.delete(session_obj)
        
        await self.session.commit()
        return count