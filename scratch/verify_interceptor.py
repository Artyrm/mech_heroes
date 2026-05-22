
import requests, json
sid = json.load(open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\session.json'))['sessionID']
payload = {
    "data": {
        "userId": 227408,
        "sessionID": sid,
        "commands": [{"commandNumber": 999999, "hash": 0, "id": "UnequipGeneralItemCommand", "paramsStr": "{}", "time": "2026-05-22T00:00:00.000Z"}],
        "clanVersion": 352498
    },
    "requestId": 12345,
    "version": "1.24.1"
}
resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/commands?userid=227408", json=payload)
print(f"Status: {resp.status_code}")
print(f"Server response: {resp.text}")
if "HashMismatch" in resp.text:
    print("!!! ТЕСТ УСПЕШЕН: Ошибка HashMismatch поймана, перехватчик сработает !!!")
