import psycopg2

def get_postgres_credentials():
    """Lädt die PostgreSQL-Zugangsdaten aus der Datenbank."""
    
    cursor = connection.cursor()
    
    cursor.execute("SELECT value FROM db_credentials WHERE key = 'db_user'")
    db_user = cursor.fetchone()[0]
    
    cursor.execute("SELECT value FROM db_credentials WHERE key = 'db_password'")
    db_password = cursor.fetchone()[0]
    
    cursor.execute("SELECT value FROM db_credentials WHERE key = 'db_host'")
    db_host = cursor.fetchone()[0]
    
    cursor.close()
    connection.close()
    
    return db_user, db_password, db_host
