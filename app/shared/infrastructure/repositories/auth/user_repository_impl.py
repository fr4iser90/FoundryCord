from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import AppUserEntity, AppRoleEntity, DiscordGuildUserEntity
from typing import Optional, List
from datetime import datetime
from app.shared.domain.repositories.auth.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[AppUserEntity]:
        result = await self.session.execute(select(AppUserEntity).where(AppUserEntity.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_discord_id(self, discord_id: str) -> Optional[AppUserEntity]:
        """Holt einen AppUserEntity anhand der Discord ID"""
        result = await self.session.execute(
            select(AppUserEntity).where(AppUserEntity.discord_id == discord_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[AppUserEntity]:
        result = await self.session.execute(select(AppUserEntity))
        return result.scalars().all()
    
    async def get_by_discord_name(self, discord_name: str) -> Optional[AppUserEntity]:
        """Holt einen AppUserEntity anhand des Discord Namens"""
        result = await self.session.execute(
            select(AppUserEntity).where(AppUserEntity.discord_name == discord_name)
        )
        return result.scalar_one_or_none()
    
    async def create(self, discord_id: str, username: str, role: str = "user") -> AppUserEntity:
        """Erstellt einen neuen AppUserEntity"""
        user = AppUserEntity(
            discord_id=discord_id,
            username=username,
            role=role
        )
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def update(self, user: AppUserEntity) -> AppUserEntity:
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def delete(self, user: AppUserEntity) -> None:
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
                select(AppUserEntity.role_id).join(AppRoleEntity).where(AppUserEntity.discord_id == discord_id)
            )
            return result.scalar_one_or_none()
    
    async def set_user_role_in_guild(self, discord_id: str, guild_id: str, role_name: str) -> bool:
        """Setzt die Rolle eines Benutzers in einer bestimmten Gilde"""
        # Hole user_id und role_id
        user_result = await self.session.execute(
            select(AppUserEntity.id).where(AppUserEntity.discord_id == discord_id)
        )
        user_id = user_result.scalar_one_or_none()
        
        role_result = await self.session.execute(
            select(AppRoleEntity.id).where(AppRoleEntity.name == role_name)
        )
        role_id = role_result.scalar_one_or_none()
        
        if not user_id or not role_id:
            return False
        
        # Prüfe, ob bereits ein Eintrag existiert
        existing = await self.session.execute(
            select(DiscordGuildUserEntity.id).where(
                DiscordGuildUserEntity.user_id == user_id, 
                DiscordGuildUserEntity.guild_id == guild_id
            )
        )
        existing_id = existing.scalar_one_or_none()
        
        if existing_id:
            # Update bestehenden Eintrag
            await self.session.execute(
                update(DiscordGuildUserEntity).where(DiscordGuildUserEntity.id == existing_id).values(
                    role_id=role_id,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            # Neuen Eintrag erstellen
            guild_user = DiscordGuildUserEntity(
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id
            )
            self.session.add(guild_user)
        
        await self.session.commit()
        return True
    
    async def create_or_update(self, user_data: dict) -> AppUserEntity:
        """Create or update a user based on discord_id"""
        try:
            # Get default role_id (assuming 'user' role exists)
            role_result = await self.session.execute(
                select(AppRoleEntity.id).where(AppRoleEntity.name == 'user')
            )
            default_role_id = role_result.scalar_one_or_none()
            
            if not default_role_id:
                # Create default role if it doesn't exist
                default_role = AppRoleEntity(name='user', description='Default user role')
                self.session.add(default_role)
                await self.session.commit()
                default_role_id = default_role.id
            
            # Check if user exists
            existing_user = await self.get_by_discord_id(str(user_data['discord_id']))
            
            if existing_user:
                # Update existing user
                existing_user.username = user_data['username']
                if 'nickname' in user_data:
                    existing_user.nickname = user_data['nickname']
                
                await self.update(existing_user)
                return existing_user
            else:
                # Create new user - entferne is_bot, es ist nicht im Entity definiert
                new_user = AppUserEntity(
                    discord_id=str(user_data['discord_id']),
                    username=user_data['username'],
                    role_id=default_role_id,  # Set default role
                    is_active=True
                )
                
                self.session.add(new_user)
                await self.session.commit()
                return new_user
                
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to create/update user: {str(e)}")
