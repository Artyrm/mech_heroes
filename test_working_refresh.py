import requests
import json
import datetime
import re

USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def get_session_and_meta():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    user_state = data['data']['userState']
    return (
        data['data']['sessionID'], 
        data['data']['clanData']['clanState']['version'],
        user_state['lastCommandId']
    )

def send_request(sid, clan_version, cmd_id, cmd_hash):
    now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
    command_body = {
        "data": {
            "userId": USER_ID,
            "sessionID": sid,
            "commands": [{
                "commandNumber": cmd_id + 1,
                "hash": cmd_hash,
                "id": "UseServiceCommand",
                "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}),
                "time": now
            }],
            "clanVersion": clan_version
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 7,
        "version": VERSION
    }
    url = f"{BASE_URL}/commands?userid={USER_ID}"
    return requests.post(url, json=command_body, headers={"Content-Type": "application/octet-stream"}, timeout=10)

# 1. Init
sid, clan_version, last_cmd_id = get_session_and_meta()

# 2. Триггер Refresh
print("Sending trigger Refresh...")
r = send_request(sid, clan_version, last_cmd_id, 1234567890)
err_msg = r.json()['data']['data'][0].get('error', {}).get('inner', {}).get('message', '')

# 3. Повтор с правильным хэшем
match = re.search(r'Hash (-?\d+) mismatch', err_msg)
if match:
    correct_hash = int(match.group(1))
    print(f"Hash identified: {correct_hash}. Sending final Refresh...")
    r = send_request(sid, clan_version, last_cmd_id, correct_hash)
    print("Final Status:", r.status_code)
    print("Final Response:", r.text)
else:
    print("Ошибка: не удалось извлечь хэш из ответа.")
    print("Response:", r.text)
