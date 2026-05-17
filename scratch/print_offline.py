import json
import os

filepath = r"g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\init_dumps\init_2026-05-17_16-55-07.json"

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

user_state = data.get('data', {}).get('userState', {})
if isinstance(user_state, str):
    user_state = json.loads(user_state)

print("offlineTimeTracker value:")
print(json.dumps(user_state.get('offlineTimeTracker'), indent=2))
