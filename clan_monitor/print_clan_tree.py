import requests
import json
import os

CONFIG_FILE = 'config.json'
SNAPSHOTS_DIR = 'snapshots'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def build_tree():
    CONF = load_json(CONFIG_FILE)
    USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
    BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
    
    # 1. Получаем иерархию
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json={"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "version": VERSION}).json()
    hier = r.get("data", {}).get("clanData", {}).get("clanState", {}).get("hierarchy", {})
    
    # 2. Получаем прирост за ночь
    f_start = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_16-16.json')
    f_end = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    d1 = load_json(f_start).get('pts', {})
    d2 = load_json(f_end).get('pts', {})
    
    def get_g(uid): return d2.get(uid, 0) - d1.get(uid, d2.get(uid, 0))

    # Карта слотов
    slots_map = {}
    leader = hier.get('leader', {})
    l_uid = str(leader.get('member', {}).get('userId'))
    slots_map[leader.get('slotId', 'leader')] = {"uid": l_uid, "nick": leader.get('member', {}).get('nickname'), "subs": []}
    
    for s in hier.get('slots', []):
        sid = s.get('slotId')
        uid = str(s.get('member', {}).get('userId'))
        slots_map[sid] = {"uid": uid, "nick": s.get('member', {}).get('nickname'), "parent": s.get('parentId'), "subs": []}

    # Строим дерево
    root = None
    for sid, data in slots_map.items():
        parent_id = data.get('parent')
        if parent_id and parent_id in slots_map:
            slots_map[parent_id]['subs'].append(sid)
        else:
            root = sid

    def print_node(sid, level=0):
        node = slots_map[sid]
        growth = get_g(node['uid'])
        print(f"{'  ' * level}- {node['nick']} (ID: {node['uid']}) | Рост: +{growth}")
        for sub_sid in node['subs']:
            print_node(sub_sid, level + 1)

    print("--- ДЕРЕВО КЛАНА И ПРИРОСТ ЗА НОЧЬ ---")
    if root: print_node(root)

if __name__ == "__main__":
    build_tree()
