import os
import sys
import argparse
import getpass
from infrastructure.logging import logger
from infrastructure.config.env_config import EnvConfig
from infrastructure.config.security.env_security import decrypt_data, generate_encryption_key

def parse_env_args():
    """Parse command line arguments for environment configuration"""
    parser = argparse.ArgumentParser(description='Homelab Discord Bot')
    parser.add_argument('--master-password', '-m', help='Master-Passwort für Entschlüsselung')
    
    # Parse known args only, so we don't interfere with other arguments
    args, _ = parser.parse_known_args()
    return args

def init_env(env_config):
    """Initialisiere Umgebungsvariablen mit einmaliger Passwortabfrage"""
    args = parse_env_args()
    
    # Pfad zur verschlüsselten Datei
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    encrypted_path = os.path.join(base_dir, ".env.encrypted")
    
    # Wenn keine verschlüsselte Datei existiert, reguläre Umgebung verwenden
    if not os.path.exists(encrypted_path):
        logger.info("Keine verschlüsselte Umgebungsdatei gefunden, verwende reguläre Variablen")
        return False
    
    # Master-Passwort entweder aus Kommandozeile oder interaktiv abfragen
    master_password = args.master_password
    if not master_password:
        # Prüfen ob interaktive Shell verfügbar
        if os.isatty(sys.stdin.fileno()):
            master_password = getpass.getpass("Master-Passwort für Entschlüsselung eingeben: ")
        else:
            logger.warning("Keine interaktive Shell vorhanden und kein Passwort angegeben")
            return False
    
    # Entschlüsselung versuchen
    if env_config.load_from_encrypted(master_password):
        # Erfolgreich entschlüsselt und geladen
        success = True
    else:
        # Entschlüsselung fehlgeschlagen, auf reguläre Umgebungsvariablen zurückfallen
        logger.warning("Entschlüsselung fehlgeschlagen, verwende reguläre Umgebungsvariablen")
        success = False
    
    # Optional: .env-Dateien entfernen nach dem Laden
    if env_config.is_production:  # Nur in Produktion
        try:
            env_files = [
                os.path.join(base_dir, "compose/.env.discordbot"),
                os.path.join(base_dir, "compose/.env.postgres")
            ]
            for file in env_files:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Removed {file} for security")
        except Exception as e:
            logger.warning(f"Could not remove env files: {e}")
    
    return success

# Nach dem Laden der Umgebung
env_config = EnvConfig()
if not init_env(env_config):
    env_config.load()
