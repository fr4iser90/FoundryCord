import nextcord
from typing import List

class TechSelector:
    """Tech interest selector for welcome dashboard"""
    
    @staticmethod
    def create_tech_select() -> nextcord.ui.StringSelect:
        """Create tech interests select dropdown"""
        return nextcord.ui.StringSelect(
            placeholder="Select your tech interests...",
            custom_id="tech_interests",
            min_values=0,
            max_values=5,
            options=[
                nextcord.SelectOption(
                    label="Linux User",
                    value="linux_user",
                    emoji="🐧",
                    description="Experienced with Linux systems"
                ),
                nextcord.SelectOption(
                    label="Docker",
                    value="docker_user",
                    emoji="🐳",
                    description="Docker container enthusiast"
                ),
                # Add other options...
            ],
            row=1
        )
