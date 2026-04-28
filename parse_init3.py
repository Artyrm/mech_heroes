import json
import re

def gather_keys():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data or 'ArenaInternal' not in res_data: continue
            
            # Find all JSON keys that are inside ArenaInternal
            # Just extract all keys in the response
            matches = set(re.findall(r'"([a-zA-Z0-9_]+)":', res_data))
            interesting = [k for k in matches if 'arena' in k.lower() or 'hist' in k.lower() or 'log' in k.lower() or 'battle' in k.lower() or 'combat' in k.lower()]
            print("Found interesting keys in init:")
            print(", ".join(interesting))

            if 'ArenaInternal' in res_data:
                idx = res_data.find('ArenaInternal')
                print("Nearby ArenaInternal ->")
                print(res_data[idx:idx+1500])
                break

if __name__ == "__main__":
    gather_keys()
