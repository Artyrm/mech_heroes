
import json
import re
import glob
import os

files = glob.glob('*.json')
target = None
for f in files:
    if 'init' in f.lower() and 'сервера' in f.lower():
        target = f
        break

if not target:
    print("File not found via glob.")
    exit(1)

print(f"Reading {target}...")
with open(target, 'r', encoding='utf-8') as f:
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
