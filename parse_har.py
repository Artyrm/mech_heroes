import json

def parse_har():
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'commands' in url or 'directcommand' in url:
            req_data = e['request'].get('postData', {}).get('text', '')
            res_data = e['response'].get('content', {}).get('text', '')
            
            # Print if it seems interesting
            if 'Arena' in req_data or 'Arena' in res_data or 'Get' in req_data or 'arena' in req_data.lower() or 'combat' in req_data.lower():
                print("== URL ==", url)
                print("== REQ ==", req_data[:500])
                print("== RES ==", res_data[:500])
                print("-" * 50)

if __name__ == '__main__':
    parse_har()
