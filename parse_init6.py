import json
import re

def inspect_userstate():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            try:
                rj = json.loads(res_data)
                u_str = rj.get('data', {}).get('userState', '')
                if u_str:
                    u_state = json.loads(u_str)
                    print("Keys in userState:", list(u_state.keys()))
                    
                    # See what looks like arena log
                    for k, v in u_state.items():
                        if 'arena' in k.lower() or 'hist' in k.lower() or 'log' in k.lower() or 'combat' in k.lower():
                            print(f"\nFOUND SUSPICIOUS KEY: {k}")
                            print(str(v)[:500])
                    
                    if 'services' in u_state:
                         print("\nKeys in userState.services:", list(u_state['services'].keys()))
                         for k, v in u_state['services'].items():
                             if 'arena' in k.lower():
                                 print(f"\nFOUND SUSPICIOUS SERVICE: {k}")
                                 print(str(v)[:500])
            except Exception as e: 
                print("Error:", e)

if __name__ == "__main__":
    inspect_userstate()
