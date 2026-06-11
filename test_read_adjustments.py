
import json
import os
from datetime import datetime, timedelta

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

# Need to find where the actual manual_adjustments.json is
# The script said 'clan_monitor/manual_adjustments.json'
adj_db = load_json('clan_monitor/manual_adjustments.json')
print(json.dumps(adj_db, indent=2))
