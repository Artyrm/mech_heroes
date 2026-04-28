import json
import re

def gather_keys():
    with open('старт игры_полный.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    for e in d['log']['entries']:
        url = e['request']['url']
        if 'init' in url:
            res_data = e['response'].get('content', {}).get('text', '')
            if not res_data: continue
            
            try:
                rj = json.loads(res_data)
                data = rj.get('data', {})
                print("Top level keys in init response:", list(data.keys()))
                
                # Try to parse stringified JSONs if present
                for k, v in data.items():
                    if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                        try:
                            v_parsed = json.loads(v)
                            if isinstance(v_parsed, dict):
                                print(f"Keys inside stringified {k}:", list(v_parsed.keys()))
                                if 'services' in v_parsed:
                                    print("Keys inside services:", list(v_parsed['services'].keys()))
                        except: pass
            except: pass

if __name__ == "__main__":
    gather_keys()
