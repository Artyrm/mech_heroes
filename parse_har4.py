import json
import re

def main():
    service_types = set()
    direct_types = set()
    history_matches = []
    
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        req_data = e['request'].get('postData', {}).get('text', '')
        res_data = e['response'].get('content', {}).get('text', '')
        
        if 'commands' in url:
            # extract service types from escaped json
            matches = re.findall(r'\\\"ServiceType\\\":\\\"(.*?)\\\"', req_data)
            for m in matches:
                service_types.add(m)
                if m == 'GetArenaHistory' or 'History' in m:
                    print("Found history command!")
        
        if 'directcommand' in url:
            try:
                rq_json = json.loads(req_data)
                dtype = rq_json.get('data', {}).get('type')
                if dtype: direct_types.add(dtype)
            except: pass
            
        if 'combat' in res_data.lower() or 'history' in res_data.lower():
            if 'directcommand' in url or 'commands' in url:
                history_matches.append((url, req_data[:200]))

    print("Service Types (/commands):", service_types)
    print("Direct Types (/directcommand):", direct_types)
    print("History/Combat keywords found in these requests:", len(history_matches))
    for m in history_matches:
        print(" ->", m[0], m[1])
    
if __name__ == "__main__":
    main()
