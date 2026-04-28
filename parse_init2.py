import json

def check_keys():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res = e['response'].get('content', {}).get('text', '')
            if res and 'ArenaInternal' in res:
                print("Found ArenaInternal in init request:", url)
                idx = res.find('ArenaInternal')
                print(res[idx:idx+1000])

if __name__ == '__main__':
    check_keys()
