import json
import re

def main():
    service_types = set()
    has_history = False
    
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'commands' in url:
            req_data = e['request'].get('postData', {}).get('text', '')
            res_data = e['response'].get('content', {}).get('text', '')
            
            # extract service types
            matches = re.findall(r'"ServiceType":"(.*?)"', req_data)
            for m in matches:
                service_types.add(m)
                
            if 'log' in res_data.lower() or 'history' in res_data.lower() or 'combat' in res_data.lower():
                # check if there's any indication of history here
                pass
                
    print("Service Types called:", service_types)
    
if __name__ == "__main__":
    main()
