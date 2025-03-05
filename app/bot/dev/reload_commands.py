import importlib
import sys
from nextcord.ext import commands
from core.decorators.auth import admin_or_higher

class ReloadCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_or_higher()
    async def reload_module(self, ctx, module_name):
        """Reloads a specific module without restarting the bot"""
        try:
            # Get the module from sys.modules
            if module_name in sys.modules:
                # Reload the module
                importlib.reload(sys.modules[module_name])
                await ctx.send(f"Module `{module_name}` reloaded successfully!")
            else:
                await ctx.send(f"Module `{module_name}` not found or not loaded.")
        except Exception as e:
            await ctx.send(f"Error reloading module: {str(e)}")

    @commands.command()
    @admin_or_higher()
    async def list_modules(self, ctx):
        """Lists all loaded modules that can be reloaded"""
        modules = [name for name in sys.modules.keys() 
                 if name.startswith('app.bot') or 
                    name.startswith('modules') or 
                    name.startswith('core')]
        
        # Format as code block
        module_list = "\n".join(modules)
        await ctx.send(f"```\nLoaded modules:\n{module_list}\n```")

def setup(bot):
    bot.add_cog(ReloadCommands(bot))