from flask import Flask, jsonify, request
import yaml
import os
from functools import wraps
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

app = Flask(__name__)

# Authentifizierung
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        # Den Token aus der .env-Datei holen
        auth_token = os.getenv('AUTH_TOKEN')
        if token != auth_token:
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/containers', methods=['GET'])
@require_auth  # Authentifizierung für diese Route
def get_containers():
    container_info = []
    base_dir = "database/docker-compose/"  # Falls dein Docker-Verzeichnis wirklich hier liegt
    if not os.path.exists(base_dir):
        return jsonify({"error": "Base directory not found"}), 500

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.yml', '.yaml')):  # Filtere nach Docker Compose-Dateien
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as stream:
                        data = yaml.safe_load(stream)  # Parse YAML-Datei
                        if data and 'services' in data:
                            for service_name, service_config in data['services'].items():
                                container_info.append({
                                    'name': service_name,
                                    'labels': service_config.get('labels', {}),
                                })
                except yaml.YAMLError as exc:
                    print(f"Fehler beim Laden von {file_path}: {exc}")
    
    return jsonify(container_info)

def run_flask():
    app.run(host='127.0.0.1', port=5000, use_reloader=False)  # Läuft auf local Schnittstellen, Port 5000
