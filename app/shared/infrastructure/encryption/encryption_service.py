from nextcord.ext import commands
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from .key_management_service import KeyManagementService
from app.shared.domain.repositories.auth.key_repository import KeyRepository

import os
import base64
import tempfile
from typing import Union, Optional
import asyncio
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class EncryptionService:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logger
        self.processed_messages = set()
        self.ready = asyncio.Event()
        self.key = None
        self.cipher = None
        self.aes_key_bytes = None
        
    async def initialize(self):
        """Async initialization to set up encryption keys"""
        try:
            # Handle Fernet encryption key
            await self._setup_fernet_key()
            
            # Handle AES encryption key
            await self._setup_aes_key()
            
            # Mark service as ready
            self.ready.set()
            logger.info("Encryption service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    async def _setup_fernet_key(self):
        """Set up Fernet key from key management service"""
        logger.info("Setting up encryption key from key management service")
        self.key_manager = KeyManagementService()
        await self.key_manager.initialize()
        self.key = self.key_manager.get_current_key()
        if not self.key:
            raise ValueError("Failed to get encryption key from key management service")
            
        # Set up Fernet cipher with our key
        self.cipher = Fernet(self.key)

    async def _setup_aes_key(self):
        """Set up AES key from key management service"""
        logger.info("Setting up AES key from key management service")
        key_repository = KeyRepository()
        await key_repository.initialize()
        aes_key = await key_repository.get_aes_key()
        if not aes_key:
            raise ValueError("Failed to get AES key from key management service")
            
        # Process the AES key
        try:
            self.aes_key_bytes = base64.urlsafe_b64decode(aes_key)
            if len(self.aes_key_bytes) != 32:
                raise ValueError("Invalid AES key length")
        except Exception as e:
            raise ValueError(f"Invalid AES key format: {str(e)}")

    async def wait_until_ready(self):
        """Wait until the service is fully initialized"""
        await self.ready.wait()

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

    async def encrypt_file(self, file_path: str) -> Optional[str]:
        """Verschlüsselt eine Datei und gibt den Pfad zur verschlüsselten Datei zurück"""
        if not os.path.exists(file_path):
            self.logger.error(f"Datei nicht gefunden: {file_path}")
            return None
            
        try:
            # Temporäre Datei für die verschlüsselte Version erstellen
            fd, encrypted_file_path = tempfile.mkstemp(suffix='.enc')
            os.close(fd)
            
            # Originaldatei lesen
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # Daten verschlüsseln
            encrypted_data = self.cipher.encrypt(file_data)
            
            # Verschlüsselte Daten in temporäre Datei schreiben
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
                
            self.logger.debug(f"Datei erfolgreich verschlüsselt: {file_path} -> {encrypted_file_path}")
            return encrypted_file_path
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Dateiverschlüsselung: {e}")
            return None
            
    async def decrypt_file(self, encrypted_file_path: str) -> Optional[str]:
        """Entschlüsselt eine Datei und gibt den Pfad zur entschlüsselten Datei zurück"""
        if not os.path.exists(encrypted_file_path):
            self.logger.error(f"Verschlüsselte Datei nicht gefunden: {encrypted_file_path}")
            return None
            
        try:
            # Temporäre Datei für die entschlüsselte Version erstellen
            fd, decrypted_file_path = tempfile.mkstemp(suffix='.dec')
            os.close(fd)
            
            # Verschlüsselte Datei lesen
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
                
            # Daten entschlüsseln
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Entschlüsselte Daten in temporäre Datei schreiben
            with open(decrypted_file_path, 'wb') as f:
                f.write(decrypted_data)
                
            self.logger.debug(f"Datei erfolgreich entschlüsselt: {encrypted_file_path} -> {decrypted_file_path}")
            return decrypted_file_path
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Dateientschlüsselung: {e}")
            return None

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

async def setup(bot):
    """Fügt den EncryptionService zum Bot hinzu"""
    encryption_service = EncryptionService(bot)
    await encryption_service.initialize()
    bot.encryption = encryption_service
    return encryption_service
