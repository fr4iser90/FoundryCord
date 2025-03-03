import functools
import nextcord
from nextcord.ext import commands
from core.auth.permissions import is_admin, is_guest, is_authorized

### --- PERMISSION DECORATORS --- ###

def admin_only():
    """Custom Decorator für Admin-Berechtigungen."""
    async def predicate(ctx):
        if not is_admin(ctx.author):
            await ctx.send("You must be an admin to use this command.")
            return False  # Verhindert die Ausführung des Befehls
        return True
    return commands.check(predicate)

def guest_only():
    """Custom Decorator für Gast-Berechtigungen, aber Admins dürfen auch teilnehmen."""
    async def predicate(ctx):
        if is_admin(ctx.author):
            return True  # Admins dürfen immer den Befehl ausführen
        if not is_guest(ctx.author):
            await ctx.send("You must be a guest to use this command.")
            return False  # Verhindert die Ausführung des Befehls für nicht-Gäste
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
