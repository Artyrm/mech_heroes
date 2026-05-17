import requests
import json
import os
import sys
import glob
import hashlib
from datetime import datetime

# Encoding fix for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.0"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def get_latest_arena_snapshot():
    snapshots = sorted(glob.glob(os.path.join("arena", "snapshots", "arena_*.json")))
    if not snapshots: return None
    with open(snapshots[-1], 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_squads():
    arena_data = get_latest_arena_snapshot()
    if not arena_data:
        print("No arena snapshot found.")
        return

    players = arena_data.get('players', [])
    user_ids = [p['userID'] for p in players]
    
    if not user_ids:
        print("No users found in latest snapshot.")
        return

    print(f"Fetching squads for {len(user_ids)} Top-50 players...")

    # 1. Start with /init to get a valid sessionID
    init_url = f"{BASE_URL}/init?userid={USER_ID}"
    init_payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    
    r = requests.post(init_url, json=init_payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"Error: /init failed with status {r.status_code}")
        return
        
    session_id = r.json().get('data', {}).get('sessionID')
    if not session_id:
        print("Error: No sessionID found.")
        return

    # 2. Get Users Raw Infos
    cmd_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
    cmd_payload = {
        "data": {
            "userId": USER_ID,
            "sessionID": session_id,
            "type": "GetUsersRawInfos",
            "request": json.dumps({"users": user_ids})
        },
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
    }

    r = requests.post(cmd_url, json=cmd_payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"Error: /directcommand failed with status {r.status_code}")
        return

    raw_resp = r.json()
    if "data" not in raw_resp or "response" not in raw_resp["data"]:
        print("Error: No valid response data in directcommand.")
        return

    inner = json.loads(raw_resp["data"]["response"])
    fetched_users = inner.get("Users", [])
    
    squads_dir = os.path.join("arena", "squads")
    os.makedirs(squads_dir, exist_ok=True)
    
    now_str = datetime.utcnow().strftime("%d-%m-%YT%H-%M-%S")
    updates_count = 0

    for u in fetched_users:
        uid = str(u.get('userId'))
        nick = u.get('nickname', 'Unknown')
        squad_str = u.get('squad')
        
        if not isinstance(squad_str, str):
            squad_str = json.dumps(squad_str, sort_keys=True)
            
        # Hash squad content to detect changes
        content_hash = hashlib.md5(squad_str.encode('utf-8')).hexdigest()
        
        user_dir = os.path.join(squads_dir, uid)
        os.makedirs(user_dir, exist_ok=True)
        
        history_file = os.path.join(user_dir, "history.json")
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
        # Check if the latest squad hash is different
        is_new = True
        if history:
            last_entry = history[-1]
            if last_entry.get('hash') == content_hash:
                is_new = False
                
        if is_new:
            # Parse squad from string to json
            squad_data = {}
            try:
                squad_data = json.loads(squad_str)
            except:
                squad_data = squad_str
                
            history.append({
                "timestamp": now_str,
                "hash": content_hash,
                "power": u.get('arenaRating', 0), # Or actual power if available, using arenaRating for now or leave out
                "squad": squad_data
            })
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            updates_count += 1
            print(f"Updated squad for {nick} ({uid})")

    print(f"Squad synchronization complete. {updates_count} new squad states recorded.")

if __name__ == "__main__":
    fetch_squads()
