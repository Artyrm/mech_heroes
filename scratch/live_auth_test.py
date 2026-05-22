
import requests, json

# Используем константы из test_api.py
USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

# 1. Авторизация (Init)
init_payload = {
    "data": {"userID": USER_ID, "authKey": AUTH_KEY},
    "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
}
init_resp = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=init_payload).json()
sid = init_resp['data']['sessionID']

# 2. Отправка команды с ошибочным хешем
cmd_payload = {
    "data": {
        "userId": USER_ID,
        "sessionID": sid,
        "commands": [{"commandNumber": 999999, "hash": 0, "id": "UnequipGeneralItemCommand", "paramsStr": "{}", "time": "22/05/2026_12:00:00.0000"}],
        "clanVersion": 352498
    },
    "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
}

resp = requests.post(f"{BASE_URL}/commands?userid={USER_ID}", json=cmd_payload)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
