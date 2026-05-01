import requests
import json
import os

CONFIG_FILE = 'clan_monitor/config.json'
CONF = json.load(open(CONFIG_FILE))
USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def find_strel_anywhere():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    
    # Сохраняем полный дамп для поиска
    with open('full_init_dump.json', 'w', encoding='utf-8') as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
        
    print("Полный дамп /init сохранен в full_init_dump.json")
    
    # Ищем Strel в тексте дампа
    dump_str = json.dumps(r, ensure_ascii=False)
    if "Strel" in dump_str:
        print("Нашел упоминание 'Strel' в дампе!")
        # Попробуем найти объект боя
        profile = r.get("data", {}).get("profile", {})
        for key, value in profile.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "Strel" in str(item):
                        print(f"Похоже на бой в поле: profile.{key}")
                        with open('battle_strel.json', 'w', encoding='utf-8') as f:
                            json.dump(item, f, indent=2, ensure_ascii=False)
                        return
    else:
        print("'Strel' не найден в /init. Пробую получить через GetArenaLog...")
        # Еще один вариант команды
        sid = r.get("data", {}).get("sessionID")
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetArenaLog", "request": "{}"}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2).json()
        with open('arena_log.json', 'w', encoding='utf-8') as f:
            json.dump(r2, f, indent=2, ensure_ascii=False)
        if "Strel" in str(r2):
             print("Нашел Strel в GetArenaLog!")

if __name__ == "__main__":
    find_strel_anywhere()
