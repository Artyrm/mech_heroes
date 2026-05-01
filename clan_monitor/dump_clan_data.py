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

def dump_all():
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json={"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "version": VERSION}).json()
    clan_data = r.get("data", {}).get("clanData", {})
    # Сохраняем в файл, чтобы не обрезалось
    with open('clan_data_full.json', 'w', encoding='utf-8') as f:
        json.dump(clan_data, f, indent=2, ensure_ascii=False)
    print("Full clan data saved to clan_data_full.json")

if __name__ == "__main__":
    dump_all()
