import json
import re

def search_text():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            keys_to_search = ['history', 'log', 'battle', 'combat', 'match']
            found = False
            for k in keys_to_search:
                matches = [m.start() for m in re.finditer(f'"{k}', res_data, re.IGNORECASE)]
                for m in matches:
                    start = max(0, m - 50)
                    end = min(len(res_data), m + 150)
                    print(f"Match for '{k}': {res_data[start:end]}")
                    found = True
            
            if found:
                break

if __name__ == "__main__":
    search_text()
