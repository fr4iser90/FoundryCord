#!/bin/sh
# compose/entrypoint.sh

set -e

# Umgebung prüfen
ENVIRONMENT="${ENVIRONMENT:-production}"

# In Produktion MUSS die verschlüsselte Variante verwendet werden
if [ "$ENVIRONMENT" = "production" ]; then
  if [ ! -f "/app/.env.encrypted" ]; then
    echo "ERROR: Production environment requires encrypted variables!"
    echo "Running environment setup script..."
    python -m infrastructure.config.security.env_security
    
    # Nach dem Setup prüfen, ob die Datei erstellt wurde
    if [ ! -f "/app/.env.encrypted" ]; then
      echo "Failed to create .env.encrypted file"
      exit 1
    fi
  fi
  
  # Wenn das Passwort schon in der Umgebung ist
  if [ -n "$MASTER_PASSWORD" ]; then
    echo "Using provided master password"
    exec python -m core.main --master-password "$MASTER_PASSWORD"
  else
    # Einmalige Passwortabfrage beim Containerstart
    echo "Please enter master password for encrypted environment:"
    read -s password
    exec python -m core.main --master-password "$password"
  fi

# In Entwicklung: Wenn verschlüsselte Datei existiert, nutze sie
elif [ -f "/app/.env.encrypted" ]; then
  echo "Found encrypted environment file"
  
  # Wenn das Passwort schon in der Umgebung ist
  if [ -n "$MASTER_PASSWORD" ]; then
    echo "Using provided master password"
    exec python -m core.main --master-password "$MASTER_PASSWORD"
  else
    # Einmalige Passwortabfrage beim Containerstart
    echo "Please enter master password for encrypted environment:"
    read -s password
    exec python -m core.main --master-password "$password"
  fi

# Normale Umgebungsvariablen verwenden (nur in Entwicklung)
else
  echo "Using regular environment variables (Development mode)"
  exec python -m core.main
fi