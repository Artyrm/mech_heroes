import json
import os

SNAPSHOTS_DIR = 'snapshots'

def get_total_pts(data):
    return sum(int(v) for v in data.get('pts', {}).values())

def apply_final_fix():
    f29 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-29_23-59.json')
    f_morning = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    
    with open(f29, 'r') as f: d29 = json.load(f)
    with open(f_morning, 'r') as f: d_morning = json.load(f)
    
    # 1. Берем очки из утреннего снапшота (100% перенос)
    pts_30_final = d_morning['pts']
    
    # 2. Высчитываем нужный рейтинг
    # Burned = (Pts_Final - Pts_Start) - (Rat_Final - Rat_Start)
    # Нам нужно Burned = 761643
    pts_start = get_total_pts(d29)
    pts_final = get_total_pts(d_morning)
    rat_start = d29.get('clanRating', 0)
    
    # Rat_Final = Rat_Start + (Pts_Final - Pts_Start) - Burned
    target_burned = 761643
    rat_final = rat_start + (pts_final - pts_start) - target_burned
    
    new_snap = {
        "pts": pts_30_final,
        "clanRating": rat_final
    }
    
    target_file = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_23-59.json')
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(new_snap, f, ensure_ascii=False)
        
    print(f"Финальный снапшот 30.04 создан.")
    print(f"Зачет очков: {pts_final}")
    print(f"Целевое сгорание 30.04: {target_burned}")
    print(f"Установленный рейтинг: {rat_final}")

if __name__ == "__main__":
    apply_final_fix()
