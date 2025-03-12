#!/usr/bin/env bash

# Prüft, ob die Docker-Dateien existieren und korrekt sind
source "./utils/config/config.sh"
source "./utils/lib/common.sh"

log_info "Überprüfe Docker-Dateien auf dem Server..."
ssh "${SERVER_USER}@${SERVER_HOST}" "ls -la ${DOCKER_DIR}/docker-compose.yml || echo 'DATEI FEHLT!'"
ssh "${SERVER_USER}@${SERVER_HOST}" "ls -la ${DOCKER_DIR}/Dockerfile || echo 'DATEI FEHLT!'" 