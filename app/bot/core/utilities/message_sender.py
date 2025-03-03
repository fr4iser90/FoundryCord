import nextcord
import os
from core.utilities.chunk_manager import chunk_message
from core.utilities.response_mode import ResponseMode, ACTIVE_RESPONSE_MODE

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
    encryption = ctx.bot.get_cog('EncryptionMiddleware')
    if not encryption:
        raise RuntimeError("Encryption middleware not loaded")
    
    encrypted_response = await encryption.encrypt_for_plugin(response)
    await ctx.send(encrypted_response, ephemeral=True)

async def send_file_response(ctx, file_path):
    if not os.path.exists(file_path):
        await ctx.send("Fehler: Datei nicht gefunden.")
        return
    
    encryption = ctx.bot.get_cog('EncryptionMiddleware')
    if encryption and ACTIVE_RESPONSE_MODE == ResponseMode.ENCRYPTED_EPHEMERAL:
        with open(file_path, 'rb') as f:
            file_data = f.read()  # Binärdaten lesen
            encrypted_data = await encryption.encrypt_for_plugin(file_data)

        encrypted_file_path = f"{file_path}.enc"
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)

        await ctx.author.send(file=nextcord.File(encrypted_file_path))
        os.remove(encrypted_file_path)
    else:
        await ctx.author.send(file=nextcord.File(file_path))

