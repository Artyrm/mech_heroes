import requests
import json
import datetime

USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def get_session_and_meta():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    user_state = data['data']['userState']
    return (
        data['data']['sessionID'], 
        data['data']['clanData']['clanState']['version'],
        user_state['lastCommandId']
    )

def send_correct_refresh(sid, clan_version, cmd_id):
    now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
    # Используем номер команды, который ожидает сервер (lastCommandId + 1)
    correct_cmd_id = cmd_id + 1
    
    command_body = {
        "data": {
            "userId": USER_ID,
            "sessionID": sid,
            "commands": [{
                "commandNumber": correct_cmd_id,
                "hash": 0, # Попробуем с нулевым или случайным, если сервер примет - отлично
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
    headers = {"Content-Type": "application/octet-stream"}
    
    print(f"Sending Refresh with Command ID: {correct_cmd_id}...")
    r = requests.post(url, json=command_body, headers=headers, timeout=10)
    return r.json()

sid, clan_version, last_cmd_id = get_session_and_meta()
resp = send_correct_refresh(sid, clan_version, last_cmd_id)
print("Response:", json.dumps(resp, indent=2, ensure_ascii=False))
