import json
import re

def search_history():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        if 'init' in e['request']['url']:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            # Let's search for enemyProfileInfo and print the context
            matches = [m.start() for m in re.finditer(r'"enemyProfileInfo"', res_data)]
            for m in matches:
                start = max(0, m - 100)
                end = min(len(res_data), m + 800)
                print(f"--- MATCH AT {m} ---")
                print(res_data[start:end])
                print("\n")

if __name__ == "__main__":
    search_history()
