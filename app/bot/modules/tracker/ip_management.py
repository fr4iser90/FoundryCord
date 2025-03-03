import os
from nextcord.ext import commands
from core.utilities.http_client import http_client

# Funktion, um die öffentliche IP zu erhalten
async def get_public_bot_ip():
    try:
        response = http_client.get('https://ipinfo.io/json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException as e:
        print(f'Error fetching public IP: {e}')
        return None

# Funktion, um den User-Hash-Link zu generieren
async def generate_ip_link(ctx):
    user_id = str(ctx.author.id)
    unique_hash = hashlib.sha256(user_id.encode()).hexdigest()
    link = f'https://tracker.XXXX.com/ip?hash={unique_hash}'
    return link

# Setup für die Bot-Kommandos
def setup(bot):
    @bot.command()
    async def ip(ctx):
        ip = await get_public_bot_ip()
        if ip:
            await ctx.send(f'Deine öffentliche IP: {ip}')
        else:
            await ctx.send('❌ Konnte die öffentliche IP nicht abrufen.')

    @bot.command()
    async def register_ip(ctx, ip: str):
        user_id = str(ctx.author.id)
        unique_hash = hashlib.sha256(user_id.encode()).hexdigest()
        tracker_url = os.getenv('TRACKER_URL')

        try:
            response = http_client.post(
                f'{tracker_url}/register',
                json={'ip': ip, 'hash': unique_hash},
                timeout=5
            )
            await ctx.send(f'✅ Deine IP {ip} wurde registriert und freigeschaltet!')
        except requests.exceptions.RequestException as e:
            await ctx.send(f'❌ Fehler beim Registrieren der IP: {str(e)}')

    @bot.command()
    async def generate_ip(ctx):
        # Link zum Registrieren der IP generieren
        link = await generate_ip_link(ctx)
        
        # Sende den Link direkt an den Benutzer
        try:
            await ctx.author.send(f'Dein IP-Tracking-Link: {link}')
            await ctx.send('✅ Ich habe dir deinen IP-Tracking-Link in einer privaten Nachricht gesendet!')
        except nextcord.errors.Forbidden:
            await ctx.send('❌ Ich konnte dir keine private Nachricht senden. Stelle sicher, dass du DMs von Servermitgliedern erlaubst.')


    @bot.command()
    async def track_ip(ctx, hash: str):
        """Der Benutzer klickt auf den Link und die IP wird durch den Bot erfasst und registriert"""
        ip = await get_public_bot_ip()
        if ip:
            user_id = str(ctx.author.id)
            unique_hash = hashlib.sha256(user_id.encode()).hexdigest()

            if hash == unique_hash:
                tracker_url = os.getenv('TRACKER_URL')

                try:
                    response = http_client.post(
                        f'{tracker_url}/register',
                        json={'ip': ip, 'hash': unique_hash},
                        timeout=5
                    )
                    await ctx.send(f'✅ Deine IP {ip} wurde erfolgreich registriert!')
                except requests.exceptions.RequestException as e:
                    await ctx.send(f'❌ Fehler beim Registrieren der IP: {str(e)}')
            else:
                await ctx.send('❌ Ungültiger Hash! Der Link stimmt nicht überein.')
        else:
            await ctx.send('❌ Konnte die öffentliche IP nicht abrufen.')