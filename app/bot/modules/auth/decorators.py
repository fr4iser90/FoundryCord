# modules/auth/decorators.py
from nextcord.ext import commands
from modules.auth.permissions import is_admin, is_guest, is_authorized

def admin_only():
    """Custom Decorator für Admin-Berechtigungen."""
    async def predicate(ctx):
        if not is_admin(ctx.author):
            await ctx.send("You must be an admin to use this command.")
            return False  # Verhindert die Ausführung des Befehls
        return True
    return commands.check(predicate)

def guest_only():
    """Custom Decorator für Gast-Berechtigungen."""
    async def predicate(ctx):
        if not is_guest(ctx.author):
            await ctx.send("You must be a guest to use this command.")
            return False  # Verhindert die Ausführung des Befehls
        return True
    return commands.check(predicate)

def authorized_only():
    """Custom Decorator für alle autorisierten Benutzer (Admins und Gäste)."""
    async def predicate(ctx):
        if not is_authorized(ctx.author):
            await ctx.send("You are not authorized to use this command.")
            return False  # Verhindert die Ausführung des Befehls
        return True
    return commands.check(predicate)