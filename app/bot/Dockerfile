FROM python:3.9-slim

WORKDIR /app/bot  # Setze den Arbeitsordner auf /app/bot

# Kopiere den gesamten Inhalt des app-Verzeichnisses in den Container
COPY ./app/bot/ /app/bot/

# Debugging-Schritt: Zeigt die Dateien im /app Verzeichnis an
RUN ls -l /app/bot

RUN ls -l /app/bot/core

RUN pip install --no-cache-dir -r /app/bot/requirements.txt
ENV PYTHONPATH=/app/bot

CMD ["python", "-m", "core.main"]


