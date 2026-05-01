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

HEADERS = {"Content-Type": "application/json"}

def check_dimarik():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
    
    hier = r.get("data", {}).get("clanData", {}).get("clanState", {}).get("hierarchy", {})
    
    dim_id = "371651"
    for i, slot in enumerate(hier.get('slots', [])):
        uid = str(slot.get('member', {}).get('userId', ''))
        if uid == dim_id:
            print(f"Димарик найден: Слот {i}, ID: {uid}, Parent: {slot.get('parentId')}")
            # Теперь ищем, чей это ParentID
            parent_slot = slot.get('parentId')
            for s in hier.get('slots', []):
                if s.get('slotId') == parent_slot:
                    p_uid = s.get('member', {}).get('userId')
                    p_nick = s.get('member', {}).get('nickname')
                    print(f"Его командир: {p_nick} (ID: {p_uid})")
                    break

if __name__ == "__main__":
    check_dimarik()
