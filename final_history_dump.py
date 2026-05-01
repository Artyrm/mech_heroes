import requests
import json
import os

CONFIG_FILE = 'clan_monitor/config.json'
CONF = json.load(open(CONFIG_FILE))
USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def final_dump():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    
    with open('current_init_dump.json', 'w', encoding='utf-8') as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
        
    arena = r.get("data", {}).get("userState", {}).get("arena", {})
    history = arena.get("battlesHistory", [])
    
    print(f"{'#':<3} | {'Время':<25} | {'Оппонент':<15} | {'Дельта'}")
    print("-" * 55)
    for i, b in enumerate(history):
        print(f"{i+1:<3} | {b.get('fightTime'):<25} | {b.get('nick'):<15} | {b.get('ourRatingDelta')}")

if __name__ == "__main__":
    final_dump()
