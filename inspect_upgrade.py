import json
with open('defs.json', 'r', encoding='utf-8') as f:
    f.readline()
    data = json.load(f)
    print(list(data.get('equipableUpgrade', {}).keys()))
