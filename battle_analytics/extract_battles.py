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

DUMPS_DIR = os.path.join(ROOT_DIR, 'init_dumps')
PYTHON_EXE = r'C:\tools\Anaconda3\python.exe'
REPORT_SCRIPT = os.path.join(ANALYTICS_DIR, 'generate_html_report.py')

def extract_for_nick(target_nick):
    print(f"INFO: Extracting battles for {target_nick}...")
    folder = os.path.join(ANALYTICS_DIR, target_nick)
    os.makedirs(folder, exist_ok=True)
    
    # Collect all json files from root and dumps
    files = []
    if os.path.exists(ROOT_DIR):
        files += [os.path.join(ROOT_DIR, f) for f in os.listdir(ROOT_DIR) if f.endswith('.json') and f != 'config.json']
    if os.path.exists(DUMPS_DIR):
        files += [os.path.join(DUMPS_DIR, f) for f in os.listdir(DUMPS_DIR) if f.endswith('.json')]
    
    found_count = 0
    new_count = 0
    
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history = []
            if 'data' in data and 'userState' in data['data']:
                history = data['data']['userState'].get('arena', {}).get('battlesHistory', [])
            elif isinstance(data, dict) and 'nick' in data:
                history = [data]
            
            for b in history:
                if b.get('nick') == target_nick:
                    found_count += 1
                    ts = int(b.get('fightTime'))
                    dt = datetime.datetime.fromtimestamp(ts)
                    date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
                    battle_id = b.get('statistics', {}).get('id', 'unknown')
                    filename = f"battle_{date_str}_{battle_id}.json"
                    filepath = os.path.join(folder, filename)
                    
                    if not os.path.exists(filepath):
                        with open(filepath, 'w', encoding='utf-8') as out:
                            json.dump(b, out, indent=2, ensure_ascii=False)
                        
                        if os.path.exists(REPORT_SCRIPT):
                            subprocess.run([PYTHON_EXE, REPORT_SCRIPT, filepath], capture_output=True)
                        new_count += 1
        except Exception as e:
            continue

    print(f"DONE: Found {found_count} battles total, {new_count} newly processed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_for_nick(sys.argv[1])
    else:
        print("Usage: python extract_battles.py <Nickname>")
