import json

with open('current_init_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract userState which is often a string inside data['data']['userState']
d = data.get('data', {})
user_state_raw = d.get('userState', '')
if isinstance(user_state_raw, str):
    us = json.loads(user_state_raw)
else:
    us = user_state_raw

generals = us.get('generals', {})
print("=== GENERALS ===")
print(json.dumps(generals, indent=2))

# Also search for item definitions if any
# Let's search for "1288", "1468", "2141", "1590", "1371", "1408" in us keys or values
target_items = [1288, 1468, 2141, 1590, 1371, 1408]
print("\n=== SEARCHING FOR ITEM IDS ===")
for k, v in us.items():
    s = str(v)
    for tid in target_items:
        if str(tid) in s:
            print(f"Found item {tid} in key '{k}': ...{s[:200]}...")
