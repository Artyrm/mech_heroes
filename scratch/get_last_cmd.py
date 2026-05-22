
import json, requests

# Используем авторизацию из test_api.py (константы)
USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

init_resp = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json={
    "data": {"userID": USER_ID, "authKey": AUTH_KEY},
    "version": VERSION, "requestId": 1, "locale": "ru", "platform": "YandexGamesDesktop"
}).json()

# Вытаскиваем LastCommandIdInternal из userState
user_state = json.loads(init_resp['data']['userState'])
last_id = user_state.get('lastCommandId')
print(f"LAST_COMMAND_ID: {last_id}")
