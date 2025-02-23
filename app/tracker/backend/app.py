from flask import Flask, request, jsonify
import hashlib
import json

app = Flask(__name__)

# Dummy-Datenbank, um die Registrierungen zu simulieren
ip_database = {}

@app.route('/register', methods=['POST'])
def register_ip():
    data = request.get_json()

    ip = data.get('ip')
    hash = data.get('hash')

    if not ip or not hash:
        return jsonify({"error": "Missing IP or hash"}), 400

    # Registriere die IP und den Hash
    ip_database[hash] = ip

    return jsonify({"message": f"IP {ip} with hash {hash} registered successfully!"}), 200

@app.route('/ip', methods=['GET'])
def get_ip():
    hash = request.args.get('hash')

    if hash not in ip_database:
        return jsonify({"error": "Hash not found"}), 404

    ip = ip_database[hash]
    return jsonify({"ip": ip, "hash": hash})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
