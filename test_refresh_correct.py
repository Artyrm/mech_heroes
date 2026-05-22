import requests
import json
import os

CONFIG_FILE = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\config.json'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    conf = json.load(f)

USER_ID = conf.get('USER_ID')
AUTH_KEY = conf.get('AUTH_KEY')
VERSION = conf.get('VERSION')
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def get_session():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    return data.get("data", {}).get("sessionID")

def test_refresh_correct():
    sid = get_session()
    if not sid:
        print("Could not get session ID")
        return

    command_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
    # Исправляем формат: JSON.stringify для поля 'request'
    command_payload = {
        "data": {
            "userId": USER_ID,
            "sessionID": sid,
            "type": "RefreshArenaLeaderboards",
            "request": json.dumps({})
        },
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
    }
    
    print(f"Sending corrected RefreshArenaLeaderboards...")
    try:
        r = requests.post(command_url, json=command_payload, headers={"Content-Type": "application/json"}, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response Content: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_refresh_correct()
