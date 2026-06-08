import os
import socket
import subprocess
import json
import time
import requests
import threading
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Глобальные переменные
xray_process = None
xray_running = False
logs = []

def add_log(msg):
    logs.append({'time': time.strftime('%H:%M:%S'), 'message': msg})
    if len(logs) > 20:
        logs.pop(0)

def get_real_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"

REAL_IP = get_real_ip()

def start_xray():
    global xray_process, xray_running
    if xray_running:
        return False
    
    # Конфиг Xray — слушает на localhost:8080, НО мы пробросим через Flask
    CONFIG = {
        "log": {
            "loglevel": "warning",
            "access": "/dev/stdout",
            "error": "/dev/stderr"
        },
        "inbounds": [
            {
                "port": 8080,
                "listen": "127.0.0.1",
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
    
    with open('/tmp/xray_config.json', 'w') as f:
        json.dump(CONFIG, f)
    
    xray_process = subprocess.Popen(
        ['xray', '-config', '/tmp/xray_config.json'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    xray_running = True
    add_log(f"VPN ЗАПУЩЕН | IP: {REAL_IP}:5000")
    return True

def stop_xray():
    global xray_process, xray_running
    if xray_process:
        xray_process.terminate()
        time.sleep(1)
        if xray_process.poll() is None:
            xray_process.kill()
        xray_process = None
    xray_running = False
    add_log("VPN ОСТАНОВЛЕН")
    return True

# ========== ГЛАВНАЯ СТРАНИЦА (МИНИМАЛИЗМ) ==========
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FreeBirdVPN</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: #0a0a2e;
            color: white;
            font-family: monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        pre {
            background: #1a1a4e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #00ff88;
            font-size: 14px;
        }
        .status { color: #ffaa44; }
        .online { color: #00ff88; }
        .offline { color: #ff4444; }
        button {
            background: #00ff88;
            border: none;
            padding: 10px 20px;
            margin-top: 20px;
            font-family: monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <pre id="content"></pre>
    <script>
        function update() {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    let html = `
╔══════════════════════════════════════╗
║         FREE BIRD VPN               ║
╠══════════════════════════════════════╣
║ Статус: ${data.vpn_running ? '✅ ЗАПУЩЕН' : '❌ ОСТАНОВЛЕН'}
║ IP сервера: ${data.server_ip}
║ Порт: 5000
║ UUID: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
║ Flow: xtls-rprx-vision
║ Path: /freebird
╠══════════════════════════════════════╣
║ <button onclick="startVPN()">▶ ЗАПУСТИТЬ</button>  <button onclick="stopVPN()">⏹ ОСТАНОВИТЬ</button>
╠══════════════════════════════════════╣
║ ЛОГИ:
${data.logs.map(l => `║ [${l.time}] ${l.message}`).join('\\n')}
╚══════════════════════════════════════╝
                    `;
                    document.getElementById('content').innerHTML = html;
                });
        }
        
        function startVPN() {
            fetch('/api/start', {method: 'POST'}).then(() => update());
        }
        
        function stopVPN() {
            fetch('/api/stop', {method: 'POST'}).then(() => update());
        }
        
        setInterval(update, 2000);
        update();
    </script>
</body>
</html>
'''

# ========== API ==========
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/status')
def status():
    return jsonify({
        'vpn_running': xray_running,
        'server_ip': REAL_IP,
        'logs': logs
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    start_xray()
    return jsonify({'success': True})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    stop_xray()
    return jsonify({'success': True})

# Прокси для WebSocket трафика Xray (через тот же порт)
@app.route('/freebird', methods=['GET', 'POST', 'UPGRADE'])
def proxy_ws():
    """Проксирует WebSocket запросы к Xray на localhost:8080"""
    import requests
    from flask import Response, stream_with_context
    
    if request.method == 'GET':
        # Проверяем, работает ли Xray
        if not xray_running:
            return "VPN not running", 503
        
        # Проксируем на локальный Xray
        try:
            req = requests.get(
                f"http://127.0.0.1:8080{request.full_path}",
                headers={k: v for k, v in request.headers if k.lower() != 'host'},
                stream=True
            )
            return Response(stream_with_context(req.iter_content(chunk_size=1024)), 
                          content_type=req.headers.get('content-type'))
        except:
            return "Xray not available", 503
    
    return '', 200

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🕊️ FREE BIRD VPN 🕊️")
    print("="*50)
    print(f"🌍 Сервер: https://freebirdvpn.onrender.com")
    print(f"📡 IP: {REAL_IP}:5000")
    print("="*50)
    print("🎯 ВСЁ НА ОДНОМ ПОРТУ 5000")
    print("🎯 Xray идут через /freebird")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000)
