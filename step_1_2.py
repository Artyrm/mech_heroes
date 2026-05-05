import os
import shutil
from datetime import datetime
import requests
import json
import subprocess

CONFIG_FILE = 'clan_monitor/config.json'
DUMPS_DIR = 'init_dumps'
ANALYTICS_DIR = 'battle_analytics'
PYTHON_EXE = r'C:\tools\Anaconda3\python.exe'

def setup():
    if not os.path.exists(DUMPS_DIR):
        os.makedirs(DUMPS_DIR)

def move_old_jsons():
    # Move root JSONs (except config) to dumps
    for f in os.listdir('.'):
        if f.endswith('.json') and f != 'config.json' and not os.path.isdir(f):
            mtime = os.path.getmtime(f)
            dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%m')
            name, ext = os.path.splitext(f)
            new_name = f"{name}_{dt}{ext}"
            shutil.move(f, os.path.join(DUMPS_DIR, new_name))
            print(f"Moved {f} to {DUMPS_DIR}/{new_name}")

def fetch_and_extract_drakon():
    with open(CONFIG_FILE, 'r') as f:
        conf = json.load(f)
    
    uid, auth, ver = conf['USER_ID'], conf['AUTH_KEY'], conf['VERSION']
    url = f"https://tanks.ya.patternmasters.ru/{ver}/init?userid={uid}"
    payload = {
        "data": {"userID": uid, "authKey": auth},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": ver
    }
    
    print(f"Fetching latest /init for LordDrakon...")
    r = requests.post(url, json=payload).json()
    
    # Save the very latest dump
    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    dump_path = os.path.join(DUMPS_DIR, f"latest_init_{now}.json")
    with open(dump_path, 'w', encoding='utf-8') as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    
    history = r.get('data', {}).get('userState', {}).get('arena', {}).get('battlesHistory', [])
    drakon_battles = [b for b in history if b.get('nick') == 'LordDrakon']
    
    if drakon_battles:
        target = drakon_battles[0]
        folder = os.path.join(ANALYTICS_DIR, 'LordDrakon')
        os.makedirs(folder, exist_ok=True)
        ft = target['fightTime'].replace('/', '-').replace(':', '-').replace('.', '_')
        path = os.path.join(folder, f"battle_{ft}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(target, f, indent=2, ensure_ascii=False)
        print(f"Saved latest battle with LordDrakon to {path}")
        # Generate report
        report_script = os.path.join(ANALYTICS_DIR, 'generate_html_report.py')
        subprocess.run([PYTHON_EXE, report_script, path])
    else:
        print("LordDrakon not found in current history.")

if __name__ == "__main__":
    setup()
    move_old_jsons()
    fetch_and_extract_drakon()
