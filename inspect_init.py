import json
import re

# Work with the compact file (972KB), not the 3.7MB formatted one
with open('Ответ на init от сервера.json', 'r', encoding='utf-8') as f:
    raw = f.read()

data = json.loads(raw)

# 1. Top-level keys
print("=== TOP-LEVEL KEYS ===")
print(list(data.keys()))

d = data.get('data', data)
print("\n=== DATA KEYS ===")
print(list(d.keys()) if isinstance(d, dict) else type(d))

# 2. Parse userState if it's a string
user_state_raw = d.get('userState', '')
if isinstance(user_state_raw, str) and user_state_raw:
    us = json.loads(user_state_raw)
    print("\n=== userState KEYS ===")
    print(sorted(us.keys()))

    # 3. Find arena-related data
    print("\n=== ARENA-RELATED TOP KEYS ===")
    for k in us.keys():
        if 'arena' in k.lower():
            v = us[k]
            print(f"  {k}: {str(v)[:200]}")
    
    # 4. Look for battle logs
    print("\n=== SEARCHING FOR BATTLE HISTORY ===")
    us_str = json.dumps(us)
    for keyword in ['battleLog', 'arenaLog', 'combatLog', 'battleHistory', 'ArenaHistory', 'RecentBattles', 'battles']:
        idx = us_str.find(f'"{keyword}"')
        if idx != -1:
            print(f"  FOUND '{keyword}' at char {idx}: ...{us_str[idx:idx+300]}...")

    # 5. Arena service
    print("\n=== ARENA SERVICE STATE ===")
    us_str2 = json.dumps(us)
    idx = us_str2.find('"ArenaInternal"')
    if idx != -1:
        print(us_str2[idx:idx+1000])
    else:
        print("  'ArenaInternal' not found in userState")
        
    # 6. My rating
    print("\n=== ARENA RATING ===")
    idx = us_str2.find('"rating"')
    while idx != -1:
        snippet = us_str2[idx:idx+80]
        if 'arenaRating' in us_str2[max(0,idx-30):idx+80] or 'Arena' in us_str2[max(0,idx-100):idx]:
            print(f"  ...{snippet}...")
        idx = us_str2.find('"rating"', idx+1)
        
elif isinstance(user_state_raw, dict):
    print("\n=== userState is already a dict, keys ===")
    print(sorted(user_state_raw.keys()))
