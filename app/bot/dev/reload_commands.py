import importlib
import sys
from nextcord.ext import commands
from app.bot.utils.decorators.auth import super_admin_or_higher, admin_or_higher
import nextcord
import os

async def setup(bot):
    # Nur im Development-Modus laden
    if os.getenv('ENVIRONMENT', 'production').lower() == 'development':
        bot.add_cog(ReloadCommands(bot))
        return True
    return False

class ReloadCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="reload",
        description="Lädt Module neu (nur im Development-Modus verfügbar)"
    )
    @super_admin_or_higher()
    async def reload(
        self, 
        interaction: nextcord.Interaction,
        extension: str = nextcord.SlashOption(
            description="Name des Moduls (leer lassen für alle Module)",
            required=False
        )
    ):
        await interaction.response.defer(ephemeral=True)
        
        if extension is None:
            # Alle Module neu laden
            success_count = 0
            error_messages = []
            
            for filename in os.listdir('./modules'):
                if filename.endswith('.py'):
                    try:
                        await self.bot.reload_extension(f'modules.{filename[:-3]}')
                        success_count += 1
                    except Exception as e:
                        error_messages.append(f'❌ {filename}: {str(e)}')
            
            response = f'✅ {success_count} Module erfolgreich neu geladen'
            if error_messages:
                response += '\n\nFehler:\n' + '\n'.join(error_messages)
            
            await interaction.followup.send(response, ephemeral=True)
        else:
            # Spezifisches Modul neu laden
            try:
                await self.bot.reload_extension(f'modules.{extension}')
                await interaction.followup.send(f'✅ Modul {extension} neu geladen', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f'❌ Fehler beim Neuladen von {extension}: {str(e)}', ephemeral=True)

    @nextcord.slash_command(
        name="reload_module",
        description="Lädt ein spezifisches Python-Modul neu"
    )
    @admin_or_higher()
    async def reload_module(
        self, 
        interaction: nextcord.Interaction,
        module_name: str = nextcord.SlashOption(
            description="Name des Python-Moduls",
            required=True
        )
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                await interaction.followup.send(f"✅ Modul `{module_name}` erfolgreich neu geladen!", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Modul `{module_name}` nicht gefunden oder nicht geladen.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Fehler beim Neuladen des Moduls: {str(e)}", ephemeral=True)

    @nextcord.slash_command(
        name="list_modules",
        description="Zeigt alle geladenen Module an"
    )
    @admin_or_higher()
    async def list_modules(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        modules = [name for name in sys.modules.keys() 
                 if name.startswith('app.bot') or 
                    name.startswith('modules') or 
                    name.startswith('core')]
        
        # Erstelle ein Embed für bessere Formatierung
        embed = nextcord.Embed(
            title="📚 Geladene Module",
            color=0x3498db
        )
        
        # Gruppiere Module nach ihrem Präfix
        grouped_modules = {
            "app.bot": [],
            "modules": [],
            "core": []
        }
        
        for module in sorted(modules):
            for prefix in grouped_modules:
                if module.startswith(prefix):
                    grouped_modules[prefix].append(module)
        
        # Füge Gruppen zum Embed hinzu
        for prefix, module_list in grouped_modules.items():
            if module_list:
                embed.add_field(
                    name=f"{prefix}",
                    value="```\n" + "\n".join(module_list) + "\n```",
                    inline=False
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)