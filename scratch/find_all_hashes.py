
import json

def find_key_recursive(obj, target_key):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target_key.lower() in k.lower():
                results.append((k, v))
            results.extend(find_key_recursive(v, target_key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_key_recursive(item, target_key))
    return results

with open('current_init_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hashes = find_key_recursive(data, 'hash')
for k, v in hashes:
    print(f"Found: {k} = {str(v)[:100]}")
