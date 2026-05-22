import requests
import json
import datetime

# Настройки
USER_ID = 227408
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

# Получаем текущий sessionID из последнего дампа
with open('init_dumps/init_2026-05-22_14-55-25.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    sid = data['data']['sessionID']
    clan_version = data['data']['clanData']['clanState']['version']

# Формируем запрос как в дампе
now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
command_body = {
    "data": {
        "userId": USER_ID,
        "sessionID": sid,
        "commands": [{
            "commandNumber": 262783, # Используем номер из примера или близкий
            "hash": 623645338,
            "id": "UseServiceCommand",
            "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}),
            "time": now
        }],
        "clanVersion": clan_version
    },
    "locale": "ru",
    "platform": "YandexGamesDesktop",
    "requestId": 2,
    "version": VERSION
}

url = f"{BASE_URL}/commands?userid={USER_ID}"
headers = {
    "Content-Type": "application/octet-stream"
}

print(f"Sending formatted Refresh request...")
try:
    r = requests.post(url, json=command_body, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
