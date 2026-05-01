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

def dump_debug():
    payload = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    print(f"Requesting {BASE_URL}/init?userid={USER_ID}...")
    resp = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=payload)
    print(f"Status Code: {resp.status_code}")
    
    try:
        data = resp.json()
        if "error" in data:
            print(f"API ERROR: {data['error']}")
        else:
            clan_data = data.get("data", {}).get("clanData", {})
            if not clan_data:
                print("No clanData in response!")
                print("Full response data keys:", data.get("data", {}).keys())
            else:
                with open('clan_data_full.json', 'w', encoding='utf-8') as f:
                    json.dump(clan_data, f, indent=2, ensure_ascii=False)
                print(f"Success! Saved {len(json.dumps(clan_data))} bytes.")
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        print("Raw Response:", resp.text[:500])

if __name__ == "__main__":
    dump_debug()
