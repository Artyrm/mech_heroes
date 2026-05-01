import requests
import json
import os

CONFIG_FILE = 'config.json'
def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

CONF = load_json(CONFIG_FILE)
USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def peek():
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json={"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "version": VERSION}).json()
    hier = r.get("data", {}).get("clanData", {}).get("clanState", {}).get("hierarchy", {})
    
    print("LEADER SLOT:")
    print(json.dumps(hier.get('leader'), indent=2, ensure_ascii=False))
    
    print("\nFIRST 3 SLOTS:")
    slots = hier.get('slots', [])
    for i in range(min(3, len(slots))):
        print(f"Slot {i}:")
        print(json.dumps(slots[i], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    peek()
