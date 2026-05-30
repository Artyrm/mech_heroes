import json
with open('defs.json', 'r', encoding='utf-8') as f:
    f.readline()
    data = json.load(f)
    generals = data.get('generals', {}).get('generals', {})
    # Get one general
    some_gen = next(iter(generals.values()))
    print(json.dumps(some_gen, indent=2))
