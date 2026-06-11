
import requests
import json
import os
import sys

import requests
import json
import os
import sys

# Load config manually
with open('clan_monitor/config.json', 'r', encoding='utf-8') as f:
    CONF = json.load(f)

USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Reuse session ID if possible
session_file = os.path.join("arena", "session.json")
session_id = None
if os.path.exists(session_file):
    with open(session_file, 'r', encoding='utf-8') as f:
        sd = json.load(f)
        session_id = sd.get('sessionID')

if not session_id:
    print("No session ID found. Need to run init first.")
    sys.exit(1)

# Pick a known player ID from registry
with open('arena/registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)
    uid = list(reg['known_users'].keys())[0] # Pick first one

print(f"Querying raw info for UID: {uid}")

cmd_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
cmd_payload = {
    "data": {
        "userId": USER_ID, "sessionID": session_id,
        "type": "GetUsersRawInfos",
        "request": json.dumps({"users": [int(uid)]})
    },
    "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
}

r = requests.post(cmd_url, json=cmd_payload, headers=HEADERS)
response = r.json()

# Save for inspection
os.makedirs('debug', exist_ok=True)
with open('debug/raw_user_info.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, indent=2, ensure_ascii=False)

print("Saved raw response to debug/raw_user_info.json")
