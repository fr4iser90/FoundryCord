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
        async def wrapper(self, ctx, *args, **kwargs):
            response = await func(self, ctx, *args, **kwargs)
            if response:
                # Use the encryption service instead of middleware
                encryption = self.bot.encryption
                if not encryption:
                    raise RuntimeError("Encryption service not loaded")
                encrypted_data = await encryption.encrypt_data(response)
                await ctx.author.send(f"🔐 Encrypted message:\n```\n{encrypted_data}\n```")
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
    """Decorator: Sends encrypted files via DM."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            file_path = await func(self, ctx, *args, **kwargs)
            
            if file_path and os.path.exists(file_path):
                # Use the encryption service instead of middleware
                encryption = self.bot.encryption
                if not encryption:
                    raise RuntimeError("Encryption service not loaded")
                
                # Read and encrypt file
                with open(file_path, 'rb') as f:
                    file_data = f.read().decode('utf-8')
                    encrypted_data = await encryption.encrypt_data(file_data)
                    encrypted_data = encrypted_data.encode('utf-8')
                
                # Create temporary encrypted file
                encrypted_file_path = f"{file_path}.enc"
                with open(encrypted_file_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Send encrypted file
                await ctx.author.send(file=nextcord.File(encrypted_file_path))
                
                # Clean up temporary file
                os.remove(encrypted_file_path)
        return wrapper
    return decorator
