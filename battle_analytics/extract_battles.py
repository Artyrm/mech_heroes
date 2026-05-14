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
                    ft_str = b.get('fightTime', '00/00/0000_00:00:00')
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
