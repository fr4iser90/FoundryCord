import os
import nextcord
import functools
from core.utilities.message_sender import send_response, send_file_response, send_encrypted_ephemeral, send_ephemeral, send_dm

def respond_in_channel():
    """Decorator: Responds directly in the channel."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                await ctx.send(response)  # Sends the response in the channel
        return wrapper
    return decorator

def respond_using_config():
    """Decorator: Responds based on the global configuration (e.g., Ephemeral, DM, etc.)."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                await send_response(ctx, response)  # Sends the response according to the global configuration
        return wrapper
    return decorator

def respond_in_dm():
    """Decorator: Responds directly via DM."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                await send_dm(ctx, response)  # Sends the response in DM
        return wrapper
    return decorator

def respond_encrypted_in_dm():
    """Decorator: Responds with encrypted content in a DM."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if response:
                await send_encrypted_ephemeral(ctx, response)  # Sends the encrypted response in DM
        return wrapper
    return decorator

def respond_with_file():
    """Decorator: Responds with a file."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            file_path = await func(ctx, *args, **kwargs)
            if file_path:
                await send_file_response(ctx, file_path)  # Sends the file as a response
        return wrapper
    return decorator

def respond_encrypted_file_in_dm():
    """Decorator: Sendet verschlüsselte Dateien per DM."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Originale Datei holen
            file_path = await func(self, ctx, *args, **kwargs)
            
            if file_path and os.path.exists(file_path):
                # Datei lesen und verschlüsseln
                with open(file_path, 'rb') as f:
                    file_data = f.read().decode('utf-8')
                    encryption = self.bot.get_cog('EncryptionMiddleware')
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
