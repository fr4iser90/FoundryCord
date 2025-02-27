import psycopg2
import os
from getpass import getpass
from core.utilities.logger import logger
from cryptography.fernet import Fernet

def check_and_setup_postgres():
    """Überprüft und richtet die PostgreSQL-Datenbank ein."""
    
    # Versuche, eine Verbindung zur PostgreSQL-Datenbank herzustellen
    try:
        connection = psycopg2.connect(
            dbname="postgres",  # Vorläufige Verbindung
            user="postgres",
            password=os.getenv('POSTGRES_PASSWORD', 'default_password'),  # Temporärer Zugang
            host="localhost"
        )
        cursor = connection.cursor()

        # Überprüfen, ob die Datenbank-Zugangsdaten bereits gesetzt sind
        cursor.execute("SELECT COUNT(*) FROM db_credentials WHERE key = 'db_user'")
        result = cursor.fetchone()

        if result[0] == 0:
            # Check environment variables first
            db_user = os.getenv('POSTGRES_USER')
            db_password = os.getenv('POSTGRES_PASSWORD')
            db_host = os.getenv('POSTGRES_HOST')
            
            if not all([db_user, db_password, db_host]):
                print("PostgreSQL-Zugangsdaten wurden noch nicht gesetzt und sind nicht in den Umgebungsvariablen vorhanden. Bitte gebe sie nun ein.")
                db_user = input("Datenbankbenutzername: ")
                db_password = getpass("Datenbankpasswort: ")
                db_host = input("Datenbank-Host (z.B. localhost): ")
            else:
                print("PostgreSQL-Zugangsdaten aus Umgebungsvariablen werden gespeichert.")
            
            # Check encryption key
            encryption_key = os.getenv('ENCRYPTION_KEY')
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY Umgebungsvariable fehlt. Bitte setzen Sie den Schlüssel.")
            
            cipher_suite = Fernet(encryption_key)
            encrypted_user = cipher_suite.encrypt(db_user.encode()).decode()
            encrypted_password = cipher_suite.encrypt(db_password.encode()).decode()
            encrypted_host = cipher_suite.encrypt(db_host.encode()).decode()

            # Zugangsdaten in der DB speichern
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS db_credentials (
                    key VARCHAR PRIMARY KEY,
                    value VARCHAR
                )
            """)
            cursor.execute(
                "INSERT INTO db_credentials (key, value) VALUES (%s, %s), (%s, %s), (%s, %s)",
                ('db_user', encrypted_user, 'db_password', encrypted_password, 'db_host', encrypted_host)
            )
            connection.commit()
            print("Zugangsdaten wurden gespeichert.")
        else:
            print("Datenbank-Zugangsdaten sind bereits gesetzt.")

        cursor.close()
        connection.close()

    except Exception as e:
        logger.error(f"Fehler beim Verbindungsaufbau zur PostgreSQL-Datenbank: {e}")
