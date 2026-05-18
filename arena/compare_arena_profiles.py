import json
import os
import glob
import sys
import requests
from datetime import datetime

# Load Config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(ROOT_DIR, 'clan_monitor', 'config.json')

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

CONF = load_config()
USER_ID = CONF['USER_ID']
AUTH_KEY = CONF['AUTH_KEY']
VERSION = CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def compare():
    # 1. Get latest snapshot
    snapshots = sorted(glob.glob(os.path.join(ROOT_DIR, "arena", "snapshots", "arena_*.json")))
    if not snapshots:
        print("No snapshots found.")
        return
    
    latest_snap = snapshots[-1]
    print(f"[*] Анализ снимка Арены: {os.path.basename(latest_snap)}")
    with open(latest_snap, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    
    players = snap.get('players', [])
    if not players:
        print("No players in snapshot.")
        return

    # Extract info from snapshot
    snap_data = {}
    uids = []
    for i, p in enumerate(players, 1):
        uid = p.get('userID')
        nick = p.get('profileState', {}).get('nickname')
        rating = int(p.get('rating', 0))
        snap_data[uid] = {'rank': i, 'nick': nick, 'rating': rating}
        uids.append(uid)

    # 2. Fetch fresh individual info
    print(f"[*] Запрос индивидуальной информации для {len(uids)} игроков...")
    
    # Get sessionID
    init_url = f"{BASE_URL}/init?userid={USER_ID}"
    init_payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    r = requests.post(init_url, json=init_payload, headers=HEADERS).json()
    session_id = r.get('data', {}).get('sessionID')
    
    if not session_id:
        print("Failed to get sessionID.")
        return

    cmd_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
    cmd_payload = {
        "data": {
            "userId": USER_ID, "sessionID": session_id,
            "type": "GetUsersRawInfos",
            "request": json.dumps({"users": uids})
        },
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
    }
    
    r2 = requests.post(cmd_url, json=cmd_payload, headers=HEADERS).json()
    fetched_users = json.loads(r2["data"]["response"]).get("Users", [])
    
    # 3. Compare
    print("\n" + "="*80)
    print(f"{'Ник':<20} | {'Место':<5} | {'Рейтинг (Арена)':<15} | {'Рейтинг (Профиль)':<15} | {'Разница'}")
    print("-" * 80)
    
    discrepancies = 0
    for u in fetched_users:
        uid = u.get('userId')
        nick = u.get('nickname')
        prof_rating = int(u.get('arenaRating', 0))
        
        s = snap_data.get(uid)
        if s:
            arena_rating = s['rating']
            diff = prof_rating - arena_rating
            if diff != 0:
                discrepancies += 1
                color_diff = f"{diff:+d}"
                print(f"{nick:<20} | {s['rank']:<5} | {arena_rating:<15} | {prof_rating:<15} | {color_diff}")
            else:
                # No difference, but maybe user wants to see all? 
                # Let's print only differences or first 5 if none
                pass
                
    if discrepancies == 0:
        print("Разночтений в рейтинге не обнаружено. Все данные синхронны.")
    else:
        print("-" * 80)
        print(f"Итого: найдено {discrepancies} несовпадений.")
    print("="*80)

if __name__ == "__main__":
    compare()
