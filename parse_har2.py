import json

def parse_har():
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'commands' in url or 'directcommand' in url:
            req_data = e['request'].get('postData', {}).get('text', '')
            res_data = e['response'].get('content', {}).get('text', '')
            
            if 'UpdateDivision' in req_data or 'RefreshArenaLeaderboards' in req_data or 'Arena' in req_data:
                print("== REQ == ", req_data)
                # Print up to 2000 chars of response to see what's in there
                print("== RES == ", res_data[:3000])
                print("-" * 50)

if __name__ == '__main__':
    parse_har()
