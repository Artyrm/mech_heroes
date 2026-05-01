import json
import os

SNAPSHOTS_DIR = 'snapshots'

def get_total_pts(data):
    return sum(int(v) for v in data.get('pts', {}).values())

def apply_precise_fix():
    # Финал 29-го (база)
    f29 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-29_23-59.json')
    # Утро 1-го (очки)
    f_morning = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    
    with open(f29, 'r') as f: d29 = json.load(f)
    with open(f_morning, 'r') as f: d_morning = json.load(f)
    
    pts_start = get_total_pts(d29)
    pts_final = get_total_pts(d_morning)
    rat_start = d29.get('clanRating', 0)
    
    # ФИКСИРУЕМ СГОРАНИЕ ВЧЕРА = 756995
    target_burned = 756995
    
    # Вычисляем рейтинг, при котором сгорание будет именно таким
    # Rat_Final = Rat_Start + (Pts_Final - Pts_Start) - Burned
    rat_final = rat_start + (pts_final - pts_start) - target_burned
    
    new_snap = {
        "pts": d_morning['pts'],
        "clanRating": rat_final
    }
    
    target_file = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_23-59.json')
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(new_snap, f, ensure_ascii=False)
        
    print(f"Финальный снапшот 30.04 зафиксирован.")
    print(f"Сгорание за вчера установлено на: {target_burned}")
    print(f"Рейтинг до сброса: {rat_final}")

if __name__ == "__main__":
    apply_precise_fix()
