import json

def go():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'patternmasters' in url and '.bundle' not in url:
            print(url.split('?')[0])

if __name__ == '__main__':
    go()
