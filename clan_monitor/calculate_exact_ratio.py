import json
import os

SNAPSHOTS_DIR = 'snapshots'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def calculate_exact_ratio():
    with open('clan_data_full.json', 'r', encoding='utf-8') as f:
        clan_data = json.load(f)
    hier = clan_data.get('clanState', {}).get('hierarchy', {})
    
    slots_by_index = {}
    leader = hier.get('leader', {})
    l_uid = str(leader.get('member', {}).get('userId'))
    # Лидер обычно имеет индекс или какой-то спец-ID. В дампе было "parent": "-1"
    slots_by_index["leader"] = {"uid": l_uid, "nick": leader.get('member', {}).get('nickname'), "children": leader.get('children', [])}
    
    for s in hier.get('slots', []):
        idx = s.get('index')
        uid = str(s.get('member', {}).get('userId'))
        slots_by_index[idx] = {"uid": uid, "nick": s.get('member', {}).get('nickname'), "children": s.get('children', [])}

    f1 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-27_23-58.json')
    f2 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-28_13-47.json')
    d1_raw = load_json(f1)
    d2_raw = load_json(f2)
    d1 = d1_raw.get('pts', {k: v for k, v in d1_raw.items() if k != 'clanRating'})
    d2 = d2_raw.get('pts', {k: v for k, v in d2_raw.items() if k != 'clanRating'})

    def get_g(uid): return int(d2.get(uid, 0)) - int(d1.get(uid, 0))

    print(f"{'Командир':<15} | {'Сумма детей':<12} | {'Рост офицера':<12} | {'%'}")
    print("-" * 60)
    
    # Проверяем лидера отдельно, если у него есть дети
    for idx, data in slots_by_index.items():
        if not data['children']: continue
        
        off_g = get_g(data['uid'])
        subs_total_g = 0
        for child_idx in data['children']:
            if child_idx in slots_by_index:
                subs_total_g += get_g(slots_by_index[child_idx]['uid'])
        
        if subs_total_g > 100:
            pct = (off_g / subs_total_g) * 100
            print(f"{data['nick'] or data['uid']:<15} | {subs_total_g:<12} | {off_g:<12} | {pct:.2f}%")

if __name__ == "__main__":
    calculate_exact_ratio()
