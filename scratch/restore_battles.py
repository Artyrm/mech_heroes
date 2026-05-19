import json
import os
import glob
import subprocess

def fix_history():
    dumps = sorted(glob.glob('init_dumps/init_*.json'))
    python_exe = r'C:\tools\Anaconda3\python.exe'
    script = 'battle_analytics/fetch_and_store_battles.py'
    
    print(f"Scanning {len(dumps)} dumps...")
    for f in dumps:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
            history = d.get('data', {}).get('userState', {}).get('arena', {}).get('battlesHistory', [])
            # Check if any new battles in this dump
            if history:
                # We just run the script for every dump, it handles duplicates itself
                print(f"Processing {os.path.basename(f)}...")
                subprocess.run([python_exe, script, '--dump', f], capture_output=True)
        except Exception as e:
            print(f"Error processing {f}: {e}")

if __name__ == "__main__":
    fix_history()
