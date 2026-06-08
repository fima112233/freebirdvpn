import os
import subprocess
import json
import time

# Конфиг Xray — слушает на порту 5000
CONFIG = {
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [
        {
            "port": 5000,
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
subprocess.Popen(
    ['xray', '-config', '/tmp/xray_config.json'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print("""
╔══════════════════════════════════════╗
║         FREE BIRD VPN               ║
║         СЕРВЕР РАБОТАЕТ             ║
╠══════════════════════════════════════╣
║ Протокол: VLESS
║ Порт: 5000
║ UUID: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
║ Flow: xtls-rprx-vision
║ Path: /freebird
║ Network: ws
╠══════════════════════════════════════╣
║ ВСЕГДА ВКЛЮЧЁН
╚══════════════════════════════════════╝
""")

# Держим процесс живым
while True:
    time.sleep(60)
