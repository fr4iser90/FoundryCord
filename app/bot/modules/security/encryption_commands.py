from nextcord.ext import commands
from core.middleware.encryption_middleware import EncryptionMiddleware

class EncryptionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encryption = EncryptionMiddleware(bot)

    @commands.command(name="encrypt")
    async def encrypt_command(self, ctx, *, message: str):
        """Verschlüsselt eine Nachricht (nur per DM)"""
        if ctx.guild:
            await ctx.send("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.")
            return
            
        encrypted = await self.encryption.encrypt_data(message)
        await ctx.author.send(f"🔐 Verschlüsselte Nachricht:\n```\n{encrypted}\n```")

    @commands.command(name="decrypt")
    async def decrypt_command(self, ctx, *, encrypted_message: str):
        """Entschlüsselt eine Nachricht (nur per DM)"""
        if ctx.guild:
            await ctx.send("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.")
            return
            
        try:
            decrypted = await self.encryption.decrypt_data(encrypted_message)
            await ctx.author.send(f"🔓 Entschlüsselte Nachricht:\n```\n{decrypted}\n```")
        except Exception as e:
            await ctx.author.send("❌ Entschlüsselung fehlgeschlagen. Ungültige Nachricht oder Schlüssel.")

def setup(bot):
    bot.add_cog(EncryptionCommands(bot))
