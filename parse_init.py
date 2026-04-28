import json

def check_init():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res = e['response'].get('content', {}).get('text', '')
            if res and 'ArenaInternal' in res:
                print("Found init request:", url)
                
                # Check for history
                idx = res.lower().find('history')
                if idx != -1:
                    print("Found 'history' key inside init!")
                    print(res[idx-50:idx+200])

if __name__ == '__main__':
    check_init()
