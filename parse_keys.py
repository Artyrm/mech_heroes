import json
import re

def gather_keys():
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'tanks' in url and ('commands' in url or 'init' in url):
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            # Find all words that look like keys in JSON
            # e.g., "BattleHistory": or "History":
            matches = re.findall(r'"([a-zA-Z0-9_]+)":', res_data)
            keys = set(matches)
            
            interesting = [k for k in keys if 'arena' in k.lower() or 'hist' in k.lower() or 'log' in k.lower() or 'battle' in k.lower() or 'combat' in k.lower()]
            if interesting:
                print("Found interesting keys in:", url)
                print(interesting)

if __name__ == "__main__":
    gather_keys()
