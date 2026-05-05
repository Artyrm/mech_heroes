import json
import os
import subprocess
import sys

CONFIG_FILE = 'clan_monitor/config.json'
DUMPS_DIR = 'init_dumps'
ANALYTICS_DIR = 'battle_analytics'
PYTHON_EXE = r'C:\tools\Anaconda3\python.exe'
REPORT_SCRIPT = os.path.join(ANALYTICS_DIR, 'generate_html_report.py')

def extract_for_nick(target_nick):
    print(f"INFO: Extracting battles for {target_nick}...")
    folder = os.path.join(ANALYTICS_DIR, target_nick)
    os.makedirs(folder, exist_ok=True)
    
    # Collect all json files from root and dumps
    files = [f for f in os.listdir('.') if f.endswith('.json') and f != 'config.json']
    if os.path.exists(DUMPS_DIR):
        files += [os.path.join(DUMPS_DIR, f) for f in os.listdir(DUMPS_DIR) if f.endswith('.json')]
    
    found_count = 0
    new_count = 0
    
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Could be a direct battle dump or a full init dump
            history = []
            if 'data' in data and 'userState' in data['data']:
                history = data['data']['userState'].get('arena', {}).get('battlesHistory', [])
            elif isinstance(data, dict) and 'nick' in data:
                history = [data]
            
            for b in history:
                if b.get('nick') == target_nick:
                    found_count += 1
                    ft_raw = b.get('fightTime', 'unknown')
                    ft = ft_raw.replace('/', '-').replace(':', '-').replace('.', '_')
                    filename = f"battle_{ft}.json"
                    filepath = os.path.join(folder, filename)
                    
                    if not os.path.exists(filepath):
                        with open(filepath, 'w', encoding='utf-8') as out:
                            json.dump(b, out, indent=2, ensure_ascii=False)
                        
                        # Run the existing report generator
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
