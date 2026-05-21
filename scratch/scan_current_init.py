
import json

with open('current_init_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def scan(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if any(word in k.lower() for word in ['key', 'salt', 'secret', 'hash', 'seed', 'token', 'auth']):
                print(f"Potential field: {new_path} = {str(v)[:100]}")
            scan(v, new_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, f"{path}[{i}]")

scan(data)
