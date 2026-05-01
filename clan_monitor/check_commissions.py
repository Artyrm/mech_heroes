import json
import os

SNAPSHOTS_DIR = 'snapshots'

def analyze_clan_growth():
    f_start = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_16-16.json')
    f_end = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    
    with open(f_start, 'r') as f: d1 = json.load(f)['pts']
    with open(f_end, 'r') as f: d2 = json.load(f)['pts']
    
    growths = {}
    for uid in d2:
        growths[uid] = d2[uid] - d1.get(uid, d2[uid])
    
    sorted_growths = sorted(growths.items(), key=lambda x: x[1], reverse=True)
    
    print(f"{'UID':<10} | {'Прирост':<10}")
    print("-" * 25)
    total_others = 0
    for uid, g in sorted_growths:
        if uid == "361914": continue # Пропускаем Александра
        print(f"{uid:<10} | {g:<10}")
        if uid != "371651": # Пропускаем и Димарика для отдельного счета
            total_others += g
            
    print("-" * 25)
    print(f"Димарик (371651): {growths.get('371651', 0)}")
    print(f"Сумма всех ОСТАЛЬНЫХ (кроме Алекса и Дима): {total_others}")
    print(f"Доля от Димарика (33%): {int(growths.get('371651', 0) * 0.33)}")
    print(f"Доля от ОСТАЛЬНЫХ (33%): {int(total_others * 0.33)}")
    print(f"ИТОГО 'пассивного' (если все под ним): {int((growths.get('371651', 0) + total_others) * 0.33)}")
    print(f"РЕАЛЬНЫЙ прирост Александра: {growths.get('361914', 0)}")

if __name__ == "__main__":
    analyze_clan_growth()
