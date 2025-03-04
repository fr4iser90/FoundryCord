FROM python:3.9-slim

WORKDIR /app/bot

# Kopiere den gesamten Inhalt des app-Verzeichnisses in den Container
COPY ./app/bot/ /app/bot/

RUN pip install --no-cache-dir -r /app/bot/requirements.txt
ENV PYTHONPATH=/app/bot

# Standard-Benutzer setzen (wird von docker-compose überschrieben, wenn dort angegeben)
USER 1001:987

CMD ["python", "-m", "core.main"]