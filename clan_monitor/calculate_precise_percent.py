import json
import os

SNAPSHOTS_DIR = 'snapshots'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def calculate_precise_percent():
    # 1. Загружаем иерархию
    with open('clan_data_full.json', 'r', encoding='utf-8') as f:
        clan_data = json.load(f)
    hier = clan_data.get('clanState', {}).get('hierarchy', {})
    
    nodes = {}
    sid_to_uid = {}
    
    leader = hier.get('leader', {})
    l_uid = str(leader.get('member', {}).get('userId'))
    l_sid = leader.get('slotId', 'leader')
    nodes[l_uid] = {"parent_sid": leader.get('parent'), "nick": leader.get('member', {}).get('nickname')}
    sid_to_uid[l_sid] = l_uid
    
    for s in hier.get('slots', []):
        sid = s.get('slotId', s.get('index')) # В иерархии может быть 'index' вместо 'slotId'
        uid = str(s.get('member', {}).get('userId'))
        nodes[uid] = {"parent_sid": s.get('parent'), "nick": s.get('member', {}).get('nickname')}
        sid_to_uid[sid] = uid

    # 2. Сравниваем снапшоты
    f1 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-27_23-58.json')
    f2 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-28_13-47.json')
    
    d1_raw = load_json(f1)
    d2_raw = load_json(f2)
    d1 = d1_raw.get('pts', {k: v for k, v in d1_raw.items() if k != 'clanRating'})
    d2 = d2_raw.get('pts', {k: v for k, v in d2_raw.items() if k != 'clanRating'})
    
    results = []
    for uid, data in nodes.items():
        p1 = int(d1.get(uid, 0))
        p2 = int(d2.get(uid, 0))
        sub_g = p2 - p1
        
        if sub_g > 100: # Берем хоть какой-то рост
            parent_sid = data['parent_sid']
            if parent_sid and parent_sid in sid_to_uid:
                p_uid = sid_to_uid[parent_sid]
                p_p1 = int(d1.get(p_uid, 0))
                p_p2 = int(d2.get(p_uid, 0))
                p_g = p_p2 - p_p1
                
                pct = (p_g / sub_g) * 100 if sub_g != 0 else 0
                results.append({
                    "sub": data['nick'] or uid,
                    "parent": nodes[p_uid]['nick'] or p_uid,
                    "sub_g": sub_g,
                    "p_g": p_g,
                    "pct": pct
                })

    print(f"{'Подчиненный':<15} | {'Командир':<15} | {'Рост П':<8} | {'Рост К':<8} | {'%'}")
    print("-" * 65)
    for r in sorted(results, key=lambda x: x['pct']):
        print(f"{r['sub']:<15} | {r['parent']:<15} | {r['sub_g']:<8} | {r['p_g']:<8} | {r['pct']:.2f}%")

if __name__ == "__main__":
    calculate_precise_percent()
