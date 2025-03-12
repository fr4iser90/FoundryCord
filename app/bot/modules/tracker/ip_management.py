import os
import hashlib
import nextcord
from nextcord.ext import commands
from app.bot.utils.http_client import http_client
from app.bot.infrastructure.logging import logger

class IPManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker_url = os.getenv('TRACKER_URL')

    async def get_public_bot_ip(self):
        """Funktion, um die öffentliche IP zu erhalten"""
        try:
            response = http_client.get('https://ipinfo.io/json')
            response.raise_for_status()
            return response.json()['ip']
        except Exception as e:
            logger.error(f'Error fetching public IP: {e}')
            return None

    async def generate_ip_link(self, user_id: str):
        """Funktion, um den User-Hash-Link zu generieren"""
        unique_hash = hashlib.sha256(user_id.encode()).hexdigest()
        return f'https://tracker.XXXX.com/ip?hash={unique_hash}'

    @commands.command()
    async def ip(self, ctx):
        """Zeigt die öffentliche IP des Bots"""
        ip = await self.get_public_bot_ip()
        if ip:
            await ctx.send(f'Deine öffentliche IP: {ip}')
        else:
            await ctx.send('❌ Konnte die öffentliche IP nicht abrufen.')

    @commands.command()
    async def register_ip(self, ctx, ip: str):
        """Registriert eine IP-Adresse"""
        user_id = str(ctx.author.id)
        unique_hash = hashlib.sha256(user_id.encode()).hexdigest()

        try:
            response = http_client.post(
                f'{self.tracker_url}/register',
                json={'ip': ip, 'hash': unique_hash},
                timeout=5
            )
            await ctx.send(f'✅ Deine IP {ip} wurde registriert und freigeschaltet!')
        except Exception as e:
            await ctx.send(f'❌ Fehler beim Registrieren der IP: {str(e)}')

    @commands.command()
    async def generate_ip(self, ctx):
        """Generiert einen IP-Tracking-Link"""
        link = await self.generate_ip_link(str(ctx.author.id))
        
        try:
            await ctx.author.send(f'Dein IP-Tracking-Link: {link}')
            await ctx.send('✅ Ich habe dir deinen IP-Tracking-Link in einer privaten Nachricht gesendet!')
        except nextcord.errors.Forbidden:
            await ctx.send('❌ Ich konnte dir keine private Nachricht senden. Stelle sicher, dass du DMs von Servermitgliedern erlaubst.')

    @commands.command()
    async def track_ip(self, ctx, hash: str):
        """Registriert die IP des Benutzers über einen Hash"""
        ip = await self.get_public_bot_ip()
        if not ip:
            await ctx.send('❌ Konnte die öffentliche IP nicht abrufen.')
            return

        user_hash = hashlib.sha256(str(ctx.author.id).encode()).hexdigest()
        if hash != user_hash:
            await ctx.send('❌ Ungültiger Hash! Der Link stimmt nicht überein.')
            return

        try:
            response = http_client.post(
                f'{self.tracker_url}/register',
                json={'ip': ip, 'hash': user_hash},
                timeout=5
            )
            await ctx.send(f'✅ Deine IP {ip} wurde erfolgreich registriert!')
        except Exception as e:
            await ctx.send(f'❌ Fehler beim Registrieren der IP: {str(e)}')

async def setup(bot):
    """Setup function for the IP management module"""
    try:
        cog = IPManagement(bot)
        bot.add_cog(cog)
        logger.info("IP Management commands initialized successfully")
        return cog
    except Exception as e:
        logger.error(f"Failed to initialize IP management: {e}")
        raise