
import requests, json, re
log = open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\logs\accountant.log', encoding='utf-8').read()
sid = re.findall(r'sessionID\":\"([^\"]+)', log)[-1]
uid = re.findall(r'userId\":(\d+)', log)[-1]

payload = {
    "data": {
        "userId": int(uid),
        "sessionID": sid,
        "commands": [{"commandNumber": 999999, "hash": 0, "id": "UnequipGeneralItemCommand", "paramsStr": "{}", "time": "22/05/2026_12:00:00.0000"}],
        "clanVersion": 352498
    },
    "locale": "ru",
    "platform": "YandexGamesDesktop",
    "requestId": 123456,
    "version": "1.24.1"
}

resp = requests.post(f"https://tanks.ya.patternmasters.ru/1.24.1/commands?userid={uid}", json=payload)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
