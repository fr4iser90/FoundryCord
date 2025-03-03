FROM python:3.9-slim

# ARGs for flexible UID/GID
ARG USER_ID
ARG GROUP_ID

# Create user dynamically based on ARGs
RUN groupadd -g ${GROUP_ID:-1000} botgroup && \
    useradd -u ${USER_ID:-1000} -g botgroup botuser

WORKDIR /app/bot

# Kopiere den gesamten Inhalt des app-Verzeichnisses in den Container
COPY ./app/bot/ /app/bot/


RUN pip install --no-cache-dir -r /app/bot/requirements.txt
ENV PYTHONPATH=/app/bot

USER ${USER_ID:-1000}:${GROUP_ID:-1000}

CMD ["python", "-m", "core.main"]