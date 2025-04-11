from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.shared.infrastructure.models import AppUserEntity, AppRoleEntity, DiscordGuildUserEntity
from typing import Optional, List
from datetime import datetime
from app.shared.domain.repositories.auth.user_repository import UserRepository
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[AppUserEntity]:
        """Fetches a user by ID, eagerly loading guild roles."""
        # Load the AppUserEntity and eagerly load the associated DiscordGuildUserEntity objects
        # and for each of those, load the associated AppRoleEntity.
        stmt = (
            select(AppUserEntity)
            .where(AppUserEntity.id == user_id)
            # Correct eager loading path: AppUserEntity -> DiscordGuildUserEntity (guild_roles) -> AppRoleEntity (role)
            .options(selectinload(AppUserEntity.guild_roles).selectinload(DiscordGuildUserEntity.role)) 
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Calculate permissions based on is_owner and loaded guild roles
            permissions = set()
            
            # Check global owner flag first
            if user.is_owner:
                permissions.add('OWNER')
                permissions.add('ADMIN') # Owners are implicitly Admins
                permissions.add('MANAGE_BOT') # Example specific owner permission
                # Add other owner permissions as needed
            
            # Add permissions from guild-specific roles
            for guild_association in user.guild_roles:
                if guild_association.role: # Check if the role relationship is loaded
                    role_name = guild_association.role.name
                    permissions.add(role_name) # Add the role name as a permission
                    # Add specific permissions based on role name if needed
                    # Example:
                    # if role_name == 'ADMIN':
                    #    permissions.add('MANAGE_USERS') 
                    #    permissions.add('MANAGE_SETTINGS')
                else:
                    logger.warning(f"Guild association found for user {user_id} in guild {guild_association.guild_id}, but role object was not loaded.")

            # Attach the calculated permissions to the user object
            user.permissions = permissions 
            logger.debug(f"Loaded user {user_id} with calculated permissions: {user.permissions}")
            
        return user
    
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
    
    async def create_or_update(self, user_data):
        """Create or update a user"""
        try:
            # Suche nach existierendem Benutzer
            discord_id = str(user_data.get('discord_id'))
            result = await self.session.execute(
                select(AppUserEntity).where(AppUserEntity.discord_id == discord_id)
            )
            user = result.scalars().first()
            
            if user:
                # Benutzer aktualisieren
                user.username = user_data.get('username')
                # Avatar-URL aktualisieren, wenn vorhanden
                if 'avatar' in user_data:
                    user.avatar = user_data.get('avatar')
            else:
                # Neuen Benutzer erstellen
                user = AppUserEntity(
                    username=user_data.get('username'),
                    discord_id=discord_id,
                    avatar=user_data.get('avatar')
                )
                self.session.add(user)
                await self.session.flush()  # Flush to get the user ID
                
                # Create guild user entry
                guild_id = str(user_data.get('guild_id'))
                if guild_id:
                    # Get default role (USER)
                    role_result = await self.session.execute(
                        select(AppRoleEntity).where(AppRoleEntity.name == 'USER')
                    )
                    role = role_result.scalars().first()
                    
                    if not role:
                        # Create role if it doesn't exist
                        role = AppRoleEntity(name='USER', description='Standard user role')
                        self.session.add(role)
                        await self.session.flush()
                    
                    guild_user = DiscordGuildUserEntity(
                        guild_id=guild_id,
                        user_id=user.id,
                        role_id=role.id  # Use same role as app user for now
                    )
                    self.session.add(guild_user)
            
            await self.session.commit()
            return user
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating/updating user: {e}")
            raise
