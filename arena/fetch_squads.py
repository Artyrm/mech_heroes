import requests
import json
import os
import sys
import glob
import hashlib
from datetime import datetime
# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arena.registry_manager as rm

# Encoding fix for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Smart path detection for config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(ROOT_DIR, 'clan_monitor', 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"CRITICAL: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
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

def is_user_active() -> bool:
    target_ip = "84.201.164.35"
    try:
        import subprocess as sp
        cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
        proc = sp.run(cmd, shell=True, capture_output=True, text=True)
        if "ESTABLISHED" in proc.stdout:
            return True
    except Exception:
        pass
    return False

def fetch_squads():
    force_run = "--force" in sys.argv
    update_history = "--update_history" in sys.argv

    # Используем реестр вместо сканирования всех файлов
    reg = rm.load_registry(force_rebuild=update_history)
    user_ids = [int(uid) for uid in reg['known_users'].keys()]
    
    if not user_ids:
        print("No users found in registry. Run with --update_history to rebuild.")
        return

    print(f"Fetching squads for {len(user_ids)} tracked players (via Registry)...")

    # 1. Try to reuse session ID
    session_id = None
    session_file = os.path.join("arena", "session.json")
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                sd = json.load(f)
                session_id = sd.get('sessionID')
        except: pass

    if not session_id:
        if is_user_active() and not force_run:
            print("[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Пропуск API-запроса в fetch_squads.py.")
            return

        print("No valid session found. Calling /init fallback...")
        init_url = f"{BASE_URL}/init?userid={USER_ID}"
        init_payload = {
            "data": {"userID": USER_ID, "authKey": AUTH_KEY},
            "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
        }
        try:
            r = requests.post(init_url, json=init_payload, headers=HEADERS, timeout=15)
            session_id = r.json().get('data', {}).get('sessionID')
        except: pass

    if not session_id:
        print("Error: No sessionID found.")
        return

    # 2. Get Users Raw Infos (Direct Command)
    if is_user_active() and not force_run:
        print("[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Пропуск /directcommand в fetch_squads.py.")
        return

    cmd_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
    cmd_payload = {
        "data": {
            "userId": USER_ID, "sessionID": session_id,
            "type": "GetUsersRawInfos",
            "request": json.dumps({"users": user_ids})
        },
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
    }

    try:
        r = requests.post(cmd_url, json=cmd_payload, headers=HEADERS, timeout=30)
        if r.status_code != 200: return
        raw_resp = r.json()
    except: return

    if "data" not in raw_resp or "response" not in raw_resp["data"]: return
    inner = json.loads(raw_resp["data"]["response"])
    fetched_users = inner.get("Users", [])
    
    squads_dir = os.path.join("arena", "squads")
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    updates_count = 0

    for u in fetched_users:
        uid = str(u.get('userId'))
        nick = u.get('nickname', 'Unknown')
        squad_str = u.get('squad')
        if not isinstance(squad_str, str):
            squad_str = json.dumps(squad_str, sort_keys=True)
            
        content_hash = hashlib.md5(squad_str.encode('utf-8')).hexdigest()
        user_dir = os.path.join(squads_dir, uid)
        os.makedirs(user_dir, exist_ok=True)
        
        # Online history
        last_visit = u.get('lastVisit')
        if last_visit:
            online_file = os.path.join(user_dir, "online_history.json")
            online_history = []
            if os.path.exists(online_file):
                try:
                    with open(online_file, 'r', encoding='utf-8') as f:
                        online_history = json.load(f)
                except: pass
            
            if not online_history or online_history[-1] != last_visit:
                online_history.append(last_visit)
                with open(online_file, 'w', encoding='utf-8') as f:
                    json.dump(online_history, f, ensure_ascii=False, indent=2)
        
        # Squad history
        history_file = os.path.join(user_dir, "history.json")
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except: pass
                
        current_rating = int(u.get('arenaRating', 0))
        is_new = True
        if history:
            last_entry = history[-1]
            if last_entry.get('hash') == content_hash and int(last_entry.get('power', 0)) == current_rating:
                is_new = False
                
        if is_new:
            try: squad_data = json.loads(squad_str)
            except: squad_data = squad_str
            history.append({"timestamp": now_str, "hash": content_hash, "power": current_rating, "squad": squad_data})
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            updates_count += 1

    print(f"Squad synchronization complete. {updates_count} new states recorded.")

if __name__ == "__main__":
    fetch_squads()
