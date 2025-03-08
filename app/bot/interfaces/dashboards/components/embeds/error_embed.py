from typing import Optional
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed

class ErrorEmbed(BaseEmbed):
    """Error specific embed implementations"""
    
    @classmethod
    def create_error(
        cls,
        title: str = "❌ Error",
        description: str = "An error occurred",
        error_code: Optional[str] = None,
        error_details: Optional[str] = None
    ) -> nextcord.Embed:
        """Creates a standardized error embed"""
        embed = cls.create(
            title=title,
            description=description,
            color=cls.ERROR_COLOR,
            timestamp=datetime.now()
        )
        
        if error_code:
            embed.add_field(
                name="Error Code",
                value=f"`{error_code}`",
                inline=True
            )
            
        if error_details:
            embed.add_field(
                name="Details",
                value=error_details,
                inline=False
            )
            
        embed.set_footer(text="Please contact an administrator if this error persists")
        return embed

    @classmethod
    def create_validation_error(
        cls,
        field_errors: dict
    ) -> nextcord.Embed:
        """Creates an embed for validation errors"""
        embed = cls.create(
            title="⚠️ Validation Error",
            description="Please check the following fields:",
            color=cls.WARNING_COLOR
        )
        
        for field, error in field_errors.items():
            embed.add_field(
                name=field.capitalize(),
                value=error,
                inline=False
            )
            
        return embed
