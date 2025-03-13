from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.models import RateLimit
from typing import Optional, List
from datetime import datetime

class RateLimitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, rate_limit_id: int) -> Optional[RateLimit]:
        result = await self.session.execute(select(RateLimit).where(RateLimit.id == rate_limit_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_and_command(self, user_id: str, command_type: str) -> Optional[RateLimit]:
        result = await self.session.execute(
            select(RateLimit).where(
                RateLimit.user_id == user_id,
                RateLimit.command_type == command_type
            )
        )
        return result.scalar_one_or_none()
    
    async def get_blocked_commands(self, user_id: str) -> List[RateLimit]:
        now = datetime.utcnow()
        result = await self.session.execute(
            select(RateLimit).where(
                RateLimit.user_id == user_id,
                RateLimit.blocked_until > now
            )
        )
        return result.scalars().all()
    
    async def create_or_update(self, user_id: str, command_type: str, 
                              increment_count: bool = True) -> RateLimit:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        now = datetime.utcnow()
        
        if rate_limit:
            rate_limit.last_attempt = now
            if increment_count:
                rate_limit.attempt_count += 1
            self.session.add(rate_limit)
        else:
            rate_limit = RateLimit(
                user_id=user_id,
                command_type=command_type,
                attempt_count=1 if increment_count else 0,
                last_attempt=now
            )
            self.session.add(rate_limit)
            
        await self.session.commit()
        return rate_limit
    
    async def set_block(self, user_id: str, command_type: str, blocked_until: datetime) -> RateLimit:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.blocked_until = blocked_until
            self.session.add(rate_limit)
            await self.session.commit()
            return rate_limit
        else:
            return await self.create_or_update(
                user_id=user_id,
                command_type=command_type,
                increment_count=False
            )
    
    async def clear_block(self, user_id: str, command_type: str) -> Optional[RateLimit]:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.blocked_until = None
            self.session.add(rate_limit)
            await self.session.commit()
            return rate_limit
        return None
    
    async def reset_count(self, user_id: str, command_type: str) -> Optional[RateLimit]:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.attempt_count = 0
            self.session.add(rate_limit)
            await self.session.commit()
            return rate_limit
        return None
    
    async def delete(self, rate_limit: RateLimit) -> None:
        await self.session.delete(rate_limit)
        await self.session.commit()