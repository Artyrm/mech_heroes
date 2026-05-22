import requests
import json
import datetime

USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

# 1. Получаем свежую сессию
def get_session():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    return data['data']['sessionID'], data['data']['clanData']['clanState']['version']

sid, clan_version = get_session()
print(f"Got fresh session: {sid}")

# 2. Выполняем Refresh в рамках этой сессии
now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
command_body = {
    "data": {
        "userId": USER_ID,
        "sessionID": sid,
        "commands": [{
            "commandNumber": 262783,
            "hash": 623645338,
            "id": "UseServiceCommand",
            "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}),
            "time": now
        }],
        "clanVersion": clan_version
    },
    "locale": "ru",
    "platform": "YandexGamesDesktop",
    "requestId": 3,
    "version": VERSION
}

url = f"{BASE_URL}/commands?userid={USER_ID}"
headers = {"Content-Type": "application/octet-stream"}

print("Sending Refresh request...")
r = requests.post(url, json=command_body, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
