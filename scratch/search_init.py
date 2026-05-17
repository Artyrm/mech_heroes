import json
import os

filepath = r"g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\init_dumps\init_2026-05-17_16-55-07.json"

if not os.path.exists(filepath):
    print("File not found")
    exit()

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Main keys:", data.keys())

user_state = data.get('data', {}).get('userState', {})
if user_state:
    if isinstance(user_state, str):
        print("userState is a string. Parsing...")
        user_state = json.loads(user_state)
    else:
        print("userState is already a dict.")
        
    print("userState keys count:", len(user_state))
    print("userState keys:", list(user_state.keys())[:10]) # show first 10 keys
    
    # Search for online/login/time
    def search_dict(d, query, path=""):
        results = []
        if isinstance(d, dict):
            for k, v in d.items():
                current_path = f"{path}.{k}" if path else k
                if query.lower() in k.lower():
                    results.append((current_path, "KEY"))
                results.extend(search_dict(v, query, current_path))
        elif isinstance(d, list):
            for i, v in enumerate(d):
                current_path = f"{path}[{i}]"
                results.extend(search_dict(v, query, current_path))
        elif isinstance(d, str):
            if query.lower() in d.lower():
                results.append((path, f"VALUE: {d[:50]}"))
        return results

    queries = ["online", "login", "offline"]
    for q in queries:
        res = search_dict(user_state, q)
        print(f"\nSearch for '{q}': found {len(res)} results")
        for r in res[:10]: # show first 10
            print(f"  {r[0]} -> {r[1]}")
            
else:
    print("userState not found in data['data']")
