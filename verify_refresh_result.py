import requests
import json
import os
import datetime

CONFIG_FILE = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\config.json'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    conf = json.load(f)

USER_ID = conf.get('USER_ID')
AUTH_KEY = conf.get('AUTH_KEY')
VERSION = "1.24.1"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def fetch_fresh_init():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    
    print(f"Fetching fresh /init to check if Refresh worked...")
    r = requests.post(url, json=payload, timeout=15)
    data = r.json()
    
    dump_path = 'init_dumps/init_after_refresh_test.json'
    with open(dump_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Dump saved to {dump_path}")
    return data

if __name__ == "__main__":
    data = fetch_fresh_init()
    arena = data.get('data', {}).get('userState', {}).get('arena', {})
    history = arena.get('battlesHistory', [])
    print(f"Battles count: {len(history)}")
    if history:
        # Сортируем последние 5
        history.sort(key=lambda x: x.get('fightTime', ''), reverse=True)
        print("Last 5 battles:")
        for b in history[:5]:
            print(f"- {b.get('nick')}: {b.get('fightTime')}")
    
    leaderboards = arena.get('leaderboards', {})
    print(f"Arena LastUpdateTime: {leaderboards.get('lastUpdateTime')}")
