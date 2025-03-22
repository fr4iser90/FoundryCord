from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.session.context import get_session
from app.shared.infrastructure.database.repositories.guild_config_repository import GuildConfigRepository
from app.shared.infrastructure.security.auth import get_current_user, User
from typing import Dict, Any, List
import json

router = APIRouter(prefix="/v1/guilds/config", tags=["guild-config"])

@router.get("/{guild_id}")
async def get_guild_config(
    guild_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get configuration for a specific guild"""
    repo = GuildConfigRepository(session)
    config = await repo.get_by_guild_id(guild_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Guild configuration not found")
    
    settings = {}
    if config.settings:
        try:
            settings = json.loads(config.settings)
        except:
            settings = {}
    
    return {
        "guild_id": config.guild_id,
        "guild_name": config.guild_name,
        "enable_categories": config.enable_categories,
        "enable_channels": config.enable_channels,
        "enable_dashboard": config.enable_dashboard,
        "enable_tasks": config.enable_tasks,
        "enable_services": config.enable_services,
        "settings": settings
    }

@router.post("/toggle-feature")
async def toggle_feature(
    data: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Toggle a feature for a specific guild"""
    guild_id = data.get("guild_id")
    feature = data.get("feature")
    enabled = data.get("enabled", False)
    
    if not guild_id or not feature:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    repo = GuildConfigRepository(session)
    config = await repo.get_by_guild_id(guild_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Guild configuration not found")
    
    # Create feature dict with only the specified feature
    features = {feature: enabled}
    
    await repo.create_or_update(
        guild_id=guild_id,
        guild_name=config.guild_name,
        features=features
    )
    
    return {"success": True}