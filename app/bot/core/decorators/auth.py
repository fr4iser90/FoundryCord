import functools
import nextcord
from nextcord.ext import commands
from core.auth.permissions import is_super_admin, is_admin, is_moderator, is_user, is_guest, is_authorized

### --- PERMISSION DECORATORS --- ###

def admin_or_higher():
    """Custom Decorator for admin or higher permissions."""
    async def predicate(ctx):
        if not is_admin(ctx.author):
            await ctx.send("You must be an admin to use this command.")
            return False
        return True
    return commands.check(predicate)

def guest_or_higher():
    """Custom Decorator for guest or higher permissions."""
    async def predicate(ctx):
        if is_admin(ctx.author):
            return True  # Admins can always use the command
        if not is_guest(ctx.author):
            await ctx.send("You must be a guest to use this command.")
            return False
        return True
    return commands.check(predicate)

def authorized_users_only():
    """Custom Decorator for all authorized users (admins and guests)."""
    async def predicate(ctx):
        if not is_authorized(ctx.author):
            await ctx.send("You are not authorized to use this command.")
            return False
        return True
    return commands.check(predicate)

def super_admin_or_higher():
    """Custom Decorator for super admin or higher permissions."""
    async def predicate(ctx):
        if not is_super_admin(ctx.author):
            await ctx.send("You must be a super admin to use this command.")
            return False
        return True
    return commands.check(predicate)

def moderator_or_higher():
    """Custom Decorator for moderator or higher permissions."""
    async def predicate(ctx):
        if is_admin(ctx.author):
            return True  # Admins can always use the command
        if not is_moderator(ctx.author):
            await ctx.send("You must be a moderator to use this command.")
            return False
        return True
    return commands.check(predicate)

def user_or_higher():
    """Custom Decorator for user or higher permissions."""
    async def predicate(ctx):
        if is_moderator(ctx.author):
            return True  # Moderators and higher can always use the command
        if not is_user(ctx.author):
            await ctx.send("You must be a user to use this command.")
            return False
        return True
    return commands.check(predicate)
