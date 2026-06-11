
import json
import glob
import os

latest_dump = sorted(glob.glob(os.path.join('init_dumps', 'init_*.json')))[-1]
print(f"Inspecting: {latest_dump}")

with open(latest_dump, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Need to drill down to find where GetUsersRawInfos response is.
# Based on fetch_squads.py, it calls GetUsersRawInfos and parses 'response' from it
# But this is an init dump.
# Let's inspect the data structure of the first player if possible.
# Wait, init dumps might not contain the detailed User info unless it's in a specific field.
# The user suggested GetUsersRawInfos, maybe I should look at a raw dump from GetUsersRawInfos if it exists?
# The script fetch_squads.py saves to arena/squads/{uid}/history.json.
# Let's check one of those instead!
squad_files = glob.glob(os.path.join('arena', 'squads', '*', 'history.json'))
if squad_files:
    with open(squad_files[0], 'r', encoding='utf-8') as f:
        hist = json.load(f)
        print(f"Structure of squad history (first entry): {json.dumps(hist[0], indent=2, ensure_ascii=False)[:500]}")
