import json

with open('defs.json', 'r', encoding='utf-8') as f:
    f.readline()
    data = json.load(f)

# Dump upgrade structure to be absolutely sure
print("--- UPGRADE SECTION ---")
print(json.dumps(data.get('generals', {}).get('upgrade', {}), indent=2))

# Check one general again for hidden base cost fields
print("\n--- GENERAL EXAMPLE ---")
some_gen_id = next(iter(data.get('generals', {}).get('generals', {}).keys()))
print(json.dumps(data.get('generals', {}).get('generals', {}).get(some_gen_id), indent=2))
