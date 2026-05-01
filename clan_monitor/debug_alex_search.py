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

def debug_hierarchy():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
    
    hier = r.get("data", {}).get("clanData", {}).get("clanState", {}).get("hierarchy", {})
    
    print(f"Leader: {hier.get('leader', {}).get('member', {}).get('nickname')} (ID: {hier.get('leader', {}).get('member', {}).get('userId')})")
    
    alex_found = False
    for i, slot in enumerate(hier.get('slots', [])):
        nick = slot.get('member', {}).get('nickname', '')
        uid = str(slot.get('member', {}).get('userId', ''))
        if "Александр" in nick or uid == "361914":
            print(f"НАЙДЕН: Слот {i}, Ник: {nick}, ID: {uid}, Роль: {slot.get('role')}, Parent: {slot.get('parentId')}, SlotID: {slot.get('slotId')}")
            alex_found = True
            
    if not alex_found:
        print("Александр не найден среди слотов.")

if __name__ == "__main__":
    debug_hierarchy()
