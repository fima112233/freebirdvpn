import os
import socket
import subprocess
import json
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# ========== FREE BIRD VPN ==========
#    Лети без границ 🕊️
# ===================================

# Конфиг Xray
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

# Запускаем Xray
subprocess.Popen(['xray', '-config', '/tmp/xray_config.json'],
                 stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL)

time.sleep(2)

SERVER_IP = socket.gethostbyname(socket.gethostname())

@app.route('/')
def index():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Логируем подключения
    with open('/tmp/freebird_logs.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {client_ip}\n")
    
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

@app.route('/ip')
def get_ip():
    return jsonify({
        'vpn': 'FreeBirdVPN',
        'server_ip': SERVER_IP,
        'port': 8080
    })

@app.route('/config')
def get_config():
    return jsonify({
        'vpn': 'FreeBirdVPN',
        'server': SERVER_IP,
        'port': 8080,
        'protocol': 'vless',
        'uuid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        'flow': 'xtls-rprx-vision',
        'network': 'ws',
        'path': '/freebird',
        'security': 'none',
        'encryption': 'none'
    })

@app.route('/logo')
def logo():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>FreeBirdVPN</title>
        <meta charset="utf-8">
        <style>
            body {
                background: linear-gradient(135deg, #0a0a2e, #1a1a4e);
                color: white;
                font-family: monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }
            .logo {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 30px;
                border: 2px solid #ffaa44;
            }
            h1 { color: #ffaa44; font-size: 48px; }
            .bird { font-size: 80px; }
            .slogan { margin-top: 20px; color: #888; }
        </style>
    </head>
    <body>
        <div class="logo">
            <div class="bird">🕊️</div>
            <h1>FreeBirdVPN</h1>
            <p>Лети без границ</p>
            <div class="slogan">Птица в небе не спрашивает разрешения</div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🕊️  FREE BIRD VPN  🕊️")
    print("="*50)
    print("    Лети без границ")
    print("="*50)
    print(f"📡 Сервер: {SERVER_IP}")
    print(f"🔌 Порт: 8080")
    print(f"🔑 UUID: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    print(f"🔄 Flow: xtls-rprx-vision")
    print(f"🌐 Path: /freebird")
    print("="*50)
    print(f"🌍 Открой в браузере: http://{SERVER_IP}:5000/logo")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000)
