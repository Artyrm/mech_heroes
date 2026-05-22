import requests
import json
import datetime
import time

CONFIG_FILE = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\config.json'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    conf = json.load(f)

USER_ID = conf.get('USER_ID')
AUTH_KEY = conf.get('AUTH_KEY')
VERSION = "1.24.1" # Используем текущую версию
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def get_session():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    return data.get("data", {}).get("sessionID"), data.get("data", {}).get("clanData", {}).get("version", 0)

def test_refresh_real():
    sid, clan_version = get_session()
    if not sid:
        print("Could not get session ID")
        return

    # Формируем тело запроса согласно вашему примеру
    now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
    
    command_body = {
        "data": {
            "userId": USER_ID,
            "sessionID": sid,
            "commands": [{
                "commandNumber": 999999, # Можно использовать случайный или инкрементируемый
                "hash": 1234567890,
                "id": "UseServiceCommand",
                "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}),
                "time": now
            }],
            "clanVersion": clan_version
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 9999999,
        "version": VERSION
    }
    
    # URL в вашем примере был .../commands?userid=...
    url = f"{BASE_URL}/commands?userid={USER_ID}"
    
    print(f"Sending real RefreshArenaLeaderboards to {url}...")
    try:
        r = requests.post(url, json=command_body, headers={"Content-Type": "application/octet-stream"}, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response Content: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_refresh_real()
