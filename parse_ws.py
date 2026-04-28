import json

def main():
    has_ws = False
    
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        if '_webSocketMessages' in e:
            has_ws = True
            print("Found WebSocket messages for URL:", e['request']['url'])
            for msg in e['_webSocketMessages']:
                data = msg.get('data', '')
                if 'Arena' in data or 'combat' in data.lower() or 'hist' in data.lower():
                    print("-->", msg['type'], data[:500])
                    print("...")
                    
    if not has_ws:
        print("No WebSockets explicitly seen with _webSocketMessages key.")
    
if __name__ == "__main__":
    main()
