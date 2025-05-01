from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import RateLimitEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from typing import Optional, List
from datetime import datetime

class RateLimitRepositoryImpl(BaseRepositoryImpl[RateLimitEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(RateLimitEntity, session)
    
    async def get_by_id(self, rate_limit_id: int) -> Optional[RateLimitEntity]:
        result = await self.session.execute(select(self.model).where(self.model.id == rate_limit_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_and_command(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        result = await self.session.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.command_type == command_type
            )
        )
        return result.scalar_one_or_none()
    
    async def get_blocked_commands(self, user_id: str) -> List[RateLimitEntity]:
        now = datetime.utcnow()
        result = await self.session.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.blocked_until > now
            )
        )
        return result.scalars().all()
    
    async def create_or_update(self, user_id: str, command_type: str, 
                              increment_count: bool = True) -> RateLimitEntity:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        now = datetime.utcnow()
        
        if rate_limit:
            rate_limit.last_attempt = now
            if increment_count:
                rate_limit.attempt_count += 1
            self.session.add(rate_limit)
        else:
            rate_limit = RateLimitEntity(
                user_id=user_id,
                command_type=command_type,
                attempt_count=1 if increment_count else 0,
                last_attempt=now
            )
            self.session.add(rate_limit)
            
        await self.session.flush()
        await self.session.refresh(rate_limit)
        return rate_limit
    
    async def set_block(self, user_id: str, command_type: str, blocked_until: datetime) -> RateLimitEntity:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.blocked_until = blocked_until
            self.session.add(rate_limit)
            await self.session.flush()
            await self.session.refresh(rate_limit)
            return rate_limit
        else:
            return await self.create_or_update(
                user_id=user_id,
                command_type=command_type,
                increment_count=False
            )
    
    async def clear_block(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.blocked_until = None
            self.session.add(rate_limit)
            await self.session.flush()
            await self.session.refresh(rate_limit)
            return rate_limit
        return None
    
    async def reset_count(self, user_id: str, command_type: str) -> Optional[RateLimitEntity]:
        rate_limit = await self.get_by_user_and_command(user_id, command_type)
        if rate_limit:
            rate_limit.attempt_count = 0
            self.session.add(rate_limit)
            await self.session.flush()
            await self.session.refresh(rate_limit)
            return rate_limit
        return None
    
    async def delete(self, rate_limit: RateLimitEntity) -> None:
        await super().delete(rate_limit)