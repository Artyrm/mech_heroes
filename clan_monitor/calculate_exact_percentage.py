import json
import os

SNAPSHOTS_DIR = 'snapshots'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def find_percentage():
    # 1. Загружаем иерархию из текущего дампа
    with open('clan_data_full.json', 'r', encoding='utf-8') as f:
        clan_data = json.load(f)
    hier = clan_data.get('clanState', {}).get('hierarchy', {})
    
    nodes = {}
    def add_node(slot):
        sid = slot.get('slotId')
        uid = str(slot.get('member', {}).get('userId'))
        nodes[uid] = {"parent_sid": slot.get('parentId')}
    
    add_node(hier.get('leader', {}))
    for s in hier.get('slots', []): add_node(s)
    
    # Карта обратной связи: SlotID -> UserID
    sid_to_uid = {}
    leader = hier.get('leader', {})
    sid_to_uid[leader.get('slotId', 'leader')] = str(leader.get('member', {}).get('userId'))
    for s in hier.get('slots', []):
        sid_to_uid[s.get('slotId')] = str(s.get('member', {}).get('userId'))

    # 2. Ищем снапшоты понедельника
    snaps = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith('points_utc_2026-04-27')])
    
    print(f"Анализируем {len(snaps)} снапшотов за понедельник...")
    
    results = []
    for i in range(len(snaps)-1):
        d1 = load_json(os.path.join(SNAPSHOTS_DIR, snaps[i])).get('pts', {})
        d2 = load_json(os.path.join(SNAPSHOTS_DIR, snaps[i+1])).get('pts', {})
        
        for uid, p2 in d2.items():
            p1 = d1.get(uid, 0)
            sub_growth = p2 - p1
            if sub_growth > 1000: # Берем заметный прирост
                parent_sid = nodes.get(uid, {}).get('parent_sid')
                if parent_sid and parent_sid in sid_to_uid:
                    parent_uid = sid_to_uid[parent_sid]
                    parent_growth = d2.get(parent_uid, 0) - d1.get(parent_uid, 0)
                    
                    if parent_growth > 0:
                        percent = (parent_growth / sub_growth) * 100
                        # Если процент подозрительно высокий (оба играли), мы это увидим
                        results.append({
                            "sub": uid,
                            "parent": parent_uid,
                            "sub_g": sub_growth,
                            "parent_g": parent_growth,
                            "pct": percent
                        })

    # Фильтруем результаты, ища минимальный процент (когда командир, вероятно, не играл сам)
    if not results:
        print("Недостаточно данных для расчета в понедельник.")
        return

    # Сортируем по проценту
    results.sort(key=lambda x: x['pct'])
    
    print(f"\n{'Подчиненный':<12} | {'Командир':<12} | {'Рост Подч.':<10} | {'Рост Ком.':<10} | {'%'}")
    print("-" * 65)
    for r in results[:10]: # Выводим топ минимальных (самых чистых) результатов
        print(f"{r['sub']:<12} | {r['parent']:<12} | {r['sub_g']:<10} | {r['parent_g']:<10} | {r['pct']:.2f}%")

if __name__ == "__main__":
    find_percentage()
