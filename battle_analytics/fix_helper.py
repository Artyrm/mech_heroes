import os, glob, json
from datetime import datetime, timedelta

def load_json(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

# Проверим генерацию и пути
print('Helper script ready')
