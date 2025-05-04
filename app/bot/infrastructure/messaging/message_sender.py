import nextcord
import os
from app.bot.infrastructure.messaging.chunk_manager import chunk_message
from app.bot.infrastructure.messaging.response_mode import ResponseMode, ACTIVE_RESPONSE_MODE

async def send_response(ctx, response):
    if not response:
        return

    if ACTIVE_RESPONSE_MODE == ResponseMode.DM:
        await send_dm(ctx, response)
    elif ACTIVE_RESPONSE_MODE == ResponseMode.EPHEMERAL:
        await send_ephemeral(ctx, response)
    elif ACTIVE_RESPONSE_MODE == ResponseMode.ENCRYPTED_EPHEMERAL:
        await send_encrypted_ephemeral(ctx, response)
    else:
        await ctx.send(response)

async def send_dm(ctx, response):
    if len(response) > 1800:
        chunks = [chunk async for chunk in chunk_message(response)]
        for chunk in chunks:
            await ctx.author.send(chunk)
    else:
        await ctx.author.send(response)

async def send_ephemeral(ctx, response):
    await ctx.send(response, ephemeral=True)

async def send_encrypted_ephemeral(ctx, response):
    encryption = ctx.bot.encryption
    if not encryption:
        raise RuntimeError("Encryption service not loaded")
    
    encrypted_response = await encryption.encrypt_data(response)
    await ctx.send(encrypted_response, ephemeral=True)

async def send_file_response(ctx, file_path):
    if not os.path.exists(file_path):
        await ctx.send("Fehler: Datei nicht gefunden.")
        return
    
    if ACTIVE_RESPONSE_MODE == ResponseMode.ENCRYPTED_EPHEMERAL:
        encryption = ctx.bot.encryption
        if not encryption:
            raise RuntimeError("Encryption service not loaded")
            
        encrypted_file_path = await encryption.encrypt_file(file_path)
        
        try:
            await ctx.author.send(file=nextcord.File(encrypted_file_path))
        finally:
            if os.path.exists(encrypted_file_path):
                os.remove(encrypted_file_path)
    else:
        await ctx.author.send(file=nextcord.File(file_path))

