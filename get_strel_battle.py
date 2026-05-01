import requests
import json
import os

CONFIG_FILE = 'clan_monitor/config.json'
def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

CONF = load_json(CONFIG_FILE)
USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {"Content-Type": "application/json"}

def get_battle_history():
    # 1. Получаем sessionID через /init
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
    sid = r.get("data", {}).get("sessionID")
    
    if not sid:
        print("Ошибка: Не удалось получить sessionID")
        return

    # 2. Запрашиваем историю боев
    # В этой игре история часто запрашивается через GetProfileData или спец. команду
    # Проверим GetArenaHistory
    p2 = {
        "data": {
            "userId": USER_ID,
            "sessionID": sid,
            "type": "GetArenaHistory",
            "request": "{}"
        },
        "platform": "YandexGamesDesktop",
        "requestId": 2,
        "version": VERSION
    }
    
    print("Запрашиваю историю арены...")
    r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
    
    history_raw = r2.get("data", {}).get("response")
    if not history_raw:
        print("История не найдена в прямом ответе. Проверяю full init...")
        # Иногда история уже есть в init.data.profile.arenaHistory
        history = r.get("data", {}).get("profile", {}).get("arenaHistory", [])
    else:
        history = json.loads(history_raw).get("history", [])

    print(f"Найдено боев: {len(history)}")
    
    target_battle = None
    for b in history:
        opp = b.get("opponent", {})
        nick = opp.get("nickname", "")
        if nick == "Strel":
            target_battle = b
            break
            
    if target_battle:
        with open('battle_strel.json', 'w', encoding='utf-8') as f:
            json.dump(target_battle, f, indent=2, ensure_ascii=False)
        print(f"Бой со Strel найден и сохранен в battle_strel.json")
        return target_battle
    else:
        print("Бой со Strel не найден в последних записях.")
        # Выведем список последних оппонентов для отладки
        print("Последние оппоненты:")
        for b in history[:5]:
            print(f"  - {b.get('opponent', {}).get('nickname')} ({b.get('result')})")

if __name__ == "__main__":
    get_battle_history()
