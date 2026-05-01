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

def find_subordinates():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
    
    d = r.get("data", {})
    hier = d.get("clanData", {}).get("clanState", {}).get("hierarchy", {})
    
    alex_id = "361914"
    # Находим слот Александра
    alex_slot_id = None
    leader = hier.get('leader', {})
    if str(leader.get('member', {}).get('userId')) == alex_id:
        alex_slot_id = leader.get('slotId')
    else:
        for slot in hier.get('slots', []):
            if str(slot.get('member', {}).get('userId')) == alex_id:
                alex_slot_id = slot.get('slotId')
                break
    
    if not alex_slot_id:
        print(f"Александр ({alex_id}) не найден в иерархии.")
        return

    print(f"Александр найден в слоте: {alex_slot_id}")
    print("Его прямые подчиненные:")
    
    subs = []
    for slot in hier.get('slots', []):
        if str(slot.get('parentId')) == alex_slot_id:
            uid = str(slot.get('member', {}).get('userId'))
            nick = slot.get('member', {}).get('nickname', 'Unknown')
            subs.append((uid, nick))
            print(f"  - {nick} (ID: {uid})")
    
    return subs

if __name__ == "__main__":
    find_subordinates()
