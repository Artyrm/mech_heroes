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

# Identity (Values from test_api.py)
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

def compute_players_hash(players):
    """Хэш по ключевым полям игроков для дедупликации по содержимому."""
    sorted_players = sorted(players, key=lambda p: p.get('userID', 0))
    hash_data = []
    for p in sorted_players:
        ps = p.get('profileState', {})
        hash_data.append(
            f"{p.get('userID')}:{p.get('rating')}:"
            f"{ps.get('winCount',0)}:{ps.get('defeatCount',0)}:"
            f"{p.get('power','0')}"
        )
    return hashlib.md5("|".join(hash_data).encode()).hexdigest()

def load_existing_hashes(snapshots_dir):
    """Загружает хэши всех существующих снимков."""
    hashes = {}
    for fpath in glob.glob(os.path.join(snapshots_dir, "arena_*.json")):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'players' in data:
                h = compute_players_hash(data['players'])
                hashes[h] = os.path.basename(fpath)
        except:
            pass
    return hashes

def fetch_arena():
    snapshots_dir = "arena/snapshots"
    os.makedirs(snapshots_dir, exist_ok=True)

    # 1. Start with /init to get a valid sessionID
    init_url = f"{BASE_URL}/init?userid={USER_ID}"
    init_payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    
    print("Connecting to game API...")
    r = requests.post(init_url, json=init_payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"Error: /init failed with status {r.status_code}")
        return
    
    init_data = r.json()
    if "error" in init_data:
        print(f"API Error: {init_data['error']}")
        return
    
    resp_data = init_data.get('data', {})
    session_id = resp_data.get('sessionID')
    user_state = resp_data.get('userState', {})
    
    if isinstance(user_state, str):
        user_state = json.loads(user_state)
    
    arena = user_state.get('arena', {})
    leaderboards = arena.get('leaderboards', {})
    players = leaderboards.get('cachedPlayers', [])
    last_update = leaderboards.get('lastUpdateTime')

    if players and last_update:
        # Дедупликация по содержимому, а не по lastUpdateTime
        content_hash = compute_players_hash(players)
        existing_hashes = load_existing_hashes(snapshots_dir)

        if content_hash in existing_hashes:
            print(f"Data unchanged (matches {existing_hashes[content_hash]}), skipping save.")
            print(f"Top-1: {players[0]['profileState']['nickname']} ({players[0]['rating']})")
        else:
            # Данные реально новые — используем текущее UTC-время для имени файла
            now_str = datetime.utcnow().strftime("%d-%m-%YT%H-%M-%S")
            target_path = os.path.join(snapshots_dir, f"arena_{now_str}.json")

            snapshot = {
                "timestamp": last_update,
                "source": "api_fetch_init",
                "content_hash": content_hash,
                "players": players
            }
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
            print(f"Saved snapshot from /init: arena_{now_str}.json")
            print(f"Top-1: {players[0]['profileState']['nickname']} ({players[0]['rating']})")
    
    if not session_id:
        print("No sessionID found, skipping /command step.")
        return

    # 2. Call RefreshArenaLeaderboards (might fail, but we already have data from /init)
    command_url = f"{BASE_URL}/command?userid={USER_ID}"
    command_payload = {
        "data": {
            "userId": USER_ID,
            "sessionID": session_id,
            "commands": [{
                "commandNumber": 100,
                "hash": 0,
                "id": "UseServiceCommand",
                "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}),
                "time": datetime.now().strftime("%d/%m/%Y_%H:%M:%S.0000")
            }],
            "clanVersion": 0
        },
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
    }

    print("Requesting latest Arena Top-50 via /command...")
    try:
        r = requests.post(command_url, json=command_payload, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            cmd_data = r.json()
            # Note: Parsing serviceChanges is complex, /init data is usually sufficient.
            print("Command RefreshArenaLeaderboards sent successfully.")
        else:
            print(f"Warning: /command failed with status {r.status_code}. Using data from /init.")
    except Exception as e:
        print(f"Warning: /command failed with error: {e}. Using data from /init.")

if __name__ == "__main__":
    fetch_arena()
