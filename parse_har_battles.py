import json
import re

def main():
    service_types = set()
    
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'commands' in url:
            req_data = e['request'].get('postData', {}).get('text', '')
            # Find ANY ServiceType mention, regardless of quoting
            # e.g., \"ServiceType\":\"UpdateDivision\"
            matches = re.findall(r'ServiceType[\\":\s]+([a-zA-Z0-9_]+)', req_data)
            for m in matches:
                service_types.add(m)
                
    print("All Service Types explicitly found in 21MB HAR:", service_types)
    
if __name__ == "__main__":
    main()
