FROM python:3.9-slim

WORKDIR /app/bot  # Setze den Arbeitsordner auf /app/bot

# Installiere systemweite Abhängigkeiten (einschließlich WireGuard-Tools)
RUN apt-get update && apt-get install -y \
    wireguard-tools \
    && rm -rf /var/lib/apt/lists/*
    
# Kopiere den gesamten Inhalt des app-Verzeichnisses in den Container
COPY ./app/bot/ /app/bot/

# Debugging-Schritt: Zeigt die Dateien im /app Verzeichnis an
RUN ls -l /app/bot

RUN ls -l /app/bot/core

RUN pip install --no-cache-dir -r /app/bot/requirements.txt
ENV PYTHONPATH=/app/bot

CMD ["python", "-m", "core.main"]


