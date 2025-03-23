from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import User, Role, GuildUser
from typing import Optional, List
from datetime import datetime
from app.shared.domain.repositories.auth.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_discord_id(self, discord_id: str) -> Optional[User]:
        """Holt einen User anhand der Discord ID"""
        result = await self.session.execute(
            select(User).where(User.discord_id == discord_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()
    
    async def get_by_discord_name(self, discord_name: str) -> Optional[User]:
        """Holt einen User anhand des Discord Namens"""
        result = await self.session.execute(
            select(User).where(User.discord_name == discord_name)
        )
        return result.scalar_one_or_none()
    
    async def create(self, discord_id: str, username: str, role: str = "user") -> User:
        """Erstellt einen neuen User"""
        user = User(
            discord_id=discord_id,
            username=username,
            role=role
        )
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()
    
    async def get_user_role_in_guild(self, discord_id: str, guild_id: str) -> Optional[str]:
        """Holt die Rolle eines Benutzers in einer bestimmten Gilde"""
        query = """
        SELECT r.name 
        FROM app_roles r
        JOIN guild_users gu ON r.id = gu.role_id
        JOIN users u ON u.id = gu.user_id
        WHERE u.discord_id = :discord_id AND gu.guild_id = :guild_id
        """
        
        result = await self.session.execute(
            text(query),
            {"discord_id": discord_id, "guild_id": guild_id}
        )
        
        role = result.scalar_one_or_none()
        if role:
            return role
        else:
            # Wenn keine gildespezifische Rolle gefunden wurde, 
            # verwende die globale Standardrolle des Benutzers
            result = await self.session.execute(
                select(User.role_id).join(Role).where(User.discord_id == discord_id)
            )
            return result.scalar_one_or_none()
    
    async def set_user_role_in_guild(self, discord_id: str, guild_id: str, role_name: str) -> bool:
        """Setzt die Rolle eines Benutzers in einer bestimmten Gilde"""
        # Hole user_id und role_id
        user_result = await self.session.execute(
            select(User.id).where(User.discord_id == discord_id)
        )
        user_id = user_result.scalar_one_or_none()
        
        role_result = await self.session.execute(
            select(Role.id).where(Role.name == role_name)
        )
        role_id = role_result.scalar_one_or_none()
        
        if not user_id or not role_id:
            return False
        
        # Prüfe, ob bereits ein Eintrag existiert
        existing = await self.session.execute(
            select(GuildUser.id).where(
                GuildUser.user_id == user_id, 
                GuildUser.guild_id == guild_id
            )
        )
        existing_id = existing.scalar_one_or_none()
        
        if existing_id:
            # Update bestehenden Eintrag
            await self.session.execute(
                update(GuildUser).where(GuildUser.id == existing_id).values(
                    role_id=role_id,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            # Neuen Eintrag erstellen
            guild_user = GuildUser(
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id
            )
            self.session.add(guild_user)
        
        await self.session.commit()
        return True
