import os
import socket
import subprocess
import json
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Конфиг Xray — слушаем на 0.0.0.0:8080
CONFIG = {
    "log": {
        "loglevel": "info",
        "access": "/dev/stdout",
        "error": "/dev/stderr"
    },
    "inbounds": [
        {
            "port": 8080,
            "protocol": "vless",
            "settings": {
                "clients": [
                    {
                        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                        "flow": "xtls-rprx-vision"
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "wsSettings": {
                    "path": "/freebird"
                }
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        }
    ]
}

# Сохраняем конфиг
with open('/tmp/xray_config.json', 'w') as f:
    json.dump(CONFIG, f)

# Запускаем Xray в фоне
proc = subprocess.Popen(['xray', '-config', '/tmp/xray_config.json'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

time.sleep(2)

SERVER_IP = socket.gethostbyname(socket.gethostname())

@app.route('/')
def index():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return jsonify({
        'vpn': 'FreeBirdVPN',
        'status': '🕊️ Лети без границ',
        'server_ip': SERVER_IP,
        'port': 8080,
        'protocol': 'vless',
        'uuid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        'flow': 'xtls-rprx-vision',
        'network': 'ws',
        'path': '/freebird',
        'your_ip': client_ip,
        'message': 'Птица в небе не спрашивает разрешения'
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🕊️  FREE BIRD VPN  🕊️")
    print("="*50)
    print("    Лети без границ")
    print("="*50)
    print(f"Сервер запущен, порт 5000 (web) и 8080 (vless)")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000)
