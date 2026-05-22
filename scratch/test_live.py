
import requests, json

# Получаем сессию из актуального файла, который бот реально использует
with open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\members_db.json', 'r', encoding='utf-8') as f:
    # Просто дергаем любой ID для примера
    data = json.load(f)
    user_id = list(data.keys())[0]

# Берем "живой" сессионный ID из лога, так как он точно рабочий
with open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\logs\accountant.log', 'r', encoding='utf-8') as f:
    log = f.read()
    # Ищем последнее вхождение sessionID
    sid_match = re.search(r'sessionID\":\"([^\"]+)', log)
    if not sid_match:
        print("SID не найден в логах")
        exit()
    sid = sid_match.group(1)

# Формируем команду с заведомо неправильным хешем 0
payload = {
    "data": {
        "userId": int(user_id),
        "sessionID": sid,
        "commands": [{"commandNumber": 999999, "hash": 0, "id": "UnequipGeneralItemCommand", "paramsStr": "{}", "time": "22/05/2026_12:00:00.0000"}],
        "clanVersion": 352498
    },
    "locale": "ru",
    "platform": "YandexGamesDesktop",
    "requestId": 123456,
    "version": "1.24.1"
}

resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/commands?userid=" + user_id, json=payload)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
