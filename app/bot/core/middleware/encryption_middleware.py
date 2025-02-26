from nextcord.ext import commands
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import logging
import base64
from typing import Union

class EncryptionMiddleware(commands.Cog):

    async def encrypt_data(self, data: str) -> str:
        """Verschlüsselt sensible Daten mit Fernet"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()

    async def decrypt_data(self, encrypted_data: str) -> str:
        """Entschlüsselt sensible Daten mit Fernet"""
        if not encrypted_data:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data.encode()).decode()
        
    def aes_encrypt(self, text: Union[str, bytes]) -> str:
        """Verschlüsselt Text mit AES-256"""
        if not text:
            return text
            
        # Convert bytes to string if needed
        if isinstance(text, bytes):
            text = text.decode('utf-8')
            
        # Generate a random 96-bit nonce
        nonce = os.urandom(12)
        
        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(self.aes_key_bytes),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt and get tag
        ciphertext = encryptor.update(text.encode()) + encryptor.finalize()
        tag = encryptor.tag
        
        # Combine nonce + tag + ciphertext
        encrypted = nonce + tag + ciphertext
        return base64.b64encode(encrypted).decode()
        
    def aes_decrypt(self, encrypted: str) -> str:
        """Entschlüsselt AES-256 verschlüsselten Text"""
        if not encrypted:
            return encrypted
            
        # Decode base64
        encrypted = base64.b64decode(encrypted)
        
        # Split into components
        nonce = encrypted[:12]
        tag = encrypted[12:28]
        ciphertext = encrypted[28:]
        
        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(self.aes_key_bytes),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        return decryptor.update(ciphertext) + decryptor.finalize()

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.processed_messages = set()  # Track processed message IDs
        
        # Fernet Key
        self.key = os.getenv('ENCRYPTION_KEY')
        if not self.key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        self.cipher = Fernet(self.key)
        
        # AES Key
        aes_key_b64 = os.getenv('AES_KEY')
        if not aes_key_b64:
            raise ValueError("AES_KEY environment variable is required")
        try:
            self.aes_key_bytes = base64.urlsafe_b64decode(aes_key_b64)
            if len(self.aes_key_bytes) != 32:
                raise ValueError("AES_KEY must be 32 bytes long after base64 decoding")
        except Exception as e:
            raise ValueError(f"Invalid AES_KEY: {str(e)}")

    async def on_message(self, message):
        """Middleware-Handler für Nachrichten"""
        # Skip if message already processed
        if message.id in self.processed_messages:
            return
        self.processed_messages.add(message.id)
        
        # Keine automatische Verschlüsselung von Nachrichten
        pass
        
    async def encrypt_for_plugin(self, text: str) -> str:
        """Verschlüsselt Text im Plugin-Format"""
        encrypted = self.aes_encrypt(text)
        return f"[ENC]{encrypted}[/ENC]"
        
    async def decrypt_from_plugin(self, text: str) -> str:
        """Entschlüsselt Plugin-Format"""
        if text.startswith('[ENC]') and text.endswith('[/ENC]'):
            encrypted = text[5:-6]
            return self.aes_decrypt(encrypted)
        return text

def setup(bot):
    """Fügt die EncryptionMiddleware zum Bot hinzu"""
    encryption_middleware = EncryptionMiddleware(bot)
    bot.add_cog(encryption_middleware)
    bot.encryption = encryption_middleware
