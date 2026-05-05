import requests
import json
import os
import subprocess
import sys
import datetime

# Smart path detection
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == 'battle_analytics':
    ROOT_DIR = os.path.dirname(SCRIPT_DIR)
    ANALYTICS_DIR = SCRIPT_DIR
else:
    ROOT_DIR = SCRIPT_DIR
    ANALYTICS_DIR = os.path.join(ROOT_DIR, 'battle_analytics')

CONFIG_FILE = os.path.join(ROOT_DIR, 'clan_monitor', 'config.json')
PYTHON_EXE = r'C:\tools\Anaconda3\python.exe'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def save_json(path, data):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_history():
    conf = load_json(CONFIG_FILE)
    user_id = conf.get('USER_ID')
    auth_key = conf.get('AUTH_KEY')
    version = conf.get('VERSION')
    
    base_url = f"https://tanks.ya.patternmasters.ru/{version}"
    
    payload = {
        "data": {"userID": user_id, "authKey": auth_key},
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 1,
        "version": version
    }
    
    print(f"DEBUG: Fetching /init for version {version}...")
    try:
        r = requests.post(f"{base_url}/init?userid={user_id}", json=payload, timeout=15).json()
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return None
    
    if r.get("errorCode") == 61058:
        new_version = r.get("errorMessage").split("version:")[1].split(")")[0].strip()
        print(f"INFO: Version outdated. Updating to {new_version}")
        conf['VERSION'] = new_version
        save_json(CONFIG_FILE, conf)
        return fetch_history()
    
    if r.get("errorCode"):
        print(f"ERROR: {r.get('errorCode')} - {r.get('errorMessage')}")
        return None
        
    history = r.get("data", {}).get("userState", {}).get("arena", {}).get("battlesHistory", [])
    print(f"INFO: Successfully fetched {len(history)} battles from history.")
    
    # Save a dump for later use (but don't output it to console)
    save_json('current_init_dump.json', r)
    
    return history

def generate_report(json_path):
    script_path = os.path.join(ANALYTICS_DIR, 'generate_html_report.py')
    if not os.path.exists(script_path):
        print(f"WARNING: Report script not found at {script_path}")
        return
    subprocess.run([PYTHON_EXE, script_path, json_path])

def process_battles(history, target_nicks):
    summary = []
    for nick in target_nicks:
        nick_battles = [b for b in history if b.get('nick') == nick]
        if not nick_battles:
            summary.append(f"{nick}: No battles found.")
            continue
            
        folder = os.path.join(ANALYTICS_DIR, nick)
        os.makedirs(folder, exist_ok=True)
        
        new_count = 0
        for b in nick_battles:
            ft_str = b.get('fightTime', '00/00/0000_00:00:00')
            # Format: DD/MM/YYYY_HH:MM:SS.mmmm
            try:
                parts = ft_str.split('_')
                date_p = parts[0].split('/')
                time_p = parts[1].split(':')
                ms = time_p[2].split('.')[1] if '.' in time_p[2] else '0000'
                date_str = f"{date_p[2]}-{date_p[1]}-{date_p[0]}_{time_p[0]}-{time_p[1]}-{time_p[2].split('.')[0]}_{ms}"
            except:
                date_str = ft_str.replace('/', '-').replace(':', '-').replace('.', '_')
            
            filename = f"battle_{date_str}.json"
            filepath = os.path.join(folder, filename)
            
            if not os.path.exists(filepath):
                save_json(filepath, b)
                generate_report(filepath)
                new_count += 1
        
        summary.append(f"{nick}: Found {len(nick_battles)} battles, {new_count} new saved and reported.")
    
    print("\n--- BATTLE PROCESSING SUMMARY ---")
    for line in summary:
        print(line)
    print("---------------------------------")

if __name__ == "__main__":
    history = fetch_history()
    if history:
        process_battles(history, ["Хоббит", "Strel"])
