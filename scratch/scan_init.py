
import json
import re

with open('Ответ на init от сервера.json', 'r', encoding='utf-8') as f:
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
    elif isinstance(obj, str):
        if len(obj) > 20 and re.match(r'^[A-Za-z0-9+/=]+$', obj):
            # Print base64-like strings
            # print(f"Base64-like: {path} = {obj[:50]}...")
            pass

scan(data)
