# core/auth/decorators.py
import os
import functools
import nextcord
from nextcord.ext import commands
from core.auth.permissions import is_admin, is_guest, is_authorized
from core.utilities.chunk_manager import chunk_message 

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

### --- OUTPUT DECORATORS --- ###

def respond_in_channel():
    """Decorator: Antwortet im aktuellen Channel."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                await ctx.send(response)
        return wrapper
    return decorator

def respond_in_dm():
    """Decorator: Antwortet per Direct Message (DM) an den Nutzer und chunkiert den Inhalt."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                # Wenn die Antwort mehr als 1800 Zeichen hat, chunkieren
                if len(response) > 1800:
                    chunks = []
                    async for chunk in chunk_message(response):
                        chunks.append(chunk)
                    # Sende jeden Chunk nacheinander
                    for chunk in chunks:
                        await ctx.author.send(chunk)
                else:
                    # Wenn die Nachricht klein genug ist, einfach senden
                    await ctx.author.send(response)
        return wrapper
    return decorator

def respond_encrypted_in_dm():
    """Decorator: Sendet verschlüsselte DMs im Plugin-Format"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                # Verschlüsseln der Nachricht
                encryption = ctx.bot.get_cog('EncryptionMiddleware')
                if not encryption:
                    raise RuntimeError("Encryption middleware not loaded")
                encrypted = await encryption.encrypt_for_plugin(response)
                
                # Wenn die Antwort mehr als 1800 Zeichen hat, chunkieren
                if len(encrypted) > 1800:
                    chunks = []
                    async for chunk in chunk_message(encrypted):
                        chunks.append(chunk)
                    # Sende jeden Chunk nacheinander
                    for chunk in chunks:
                        await ctx.author.send(chunk)
                else:
                    # Wenn die Nachricht klein genug ist, einfach senden
                    await ctx.author.send(encrypted)
        return wrapper
    return decorator

def respond_in_dm_in_codeblock():
    """Decorator: Antwortet per Direct Message (DM) an den Nutzer und chunkiert den Inhalt mit Codeblock-Formatierung."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            if not hasattr(ctx, '_already_responded'):
                response = await func(ctx, *args, **kwargs)
                if response:
                    # Wenn die Antwort mehr als 1800 Zeichen hat, chunkieren
                    if len(response) > 1800:
                        chunks = [f"```{chunk}```" for chunk in chunk_message(response)]  # Codeblock um jedes Chunk legen
                        for chunk in chunks:
                            await ctx.author.send(chunk)
                    else:
                        # Die Antwort immer in einen Codeblock setzen
                        await ctx.author.send(f"```{response}```")
                    ctx._already_responded = True
        return wrapper
    return decorator

def respond_encrypted_file_in_dm():
    """Decorator: Sendet verschlüsselte Dateien per DM."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # Originale Datei holen
            file_path = await func(ctx, *args, **kwargs)
            
            if file_path and os.path.exists(file_path):
                # Datei lesen und verschlüsseln
                with open(file_path, 'rb') as f:
                    file_data = f.read().decode('utf-8')
                    encryption = ctx.bot.get_cog('EncryptionMiddleware')
                    if not encryption:
                        raise RuntimeError("Encryption middleware not loaded")
                    encrypted_data = await encryption.encrypt_for_plugin(file_data)
                    encrypted_data = encrypted_data.encode('utf-8')  # Convert back to bytes for file writing
                
                # Temporäre verschlüsselte Datei erstellen
                encrypted_file_path = f"{file_path}.enc"
                with open(encrypted_file_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Verschlüsselte Datei senden
                await ctx.author.send(file=nextcord.File(encrypted_file_path))
                
                # Temporäre Datei löschen
                os.remove(encrypted_file_path)
        return wrapper
    return decorator
