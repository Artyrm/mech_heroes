import json

def extract_userstate():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        if 'init' in e['request']['url']:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            try:
                rj = json.loads(res_data)
                u_str = rj.get('data', {}).get('userState', '')
                if u_str:
                    u_state = json.loads(u_str)
                    
                    # Write formatted JSON to file for inspection
                    with open('userState.json', 'w', encoding='utf-8') as out:
                        json.dump(u_state, out, indent=2, ensure_ascii=False)
                    print("Wrote userState.json")
                    return
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    extract_userstate()
