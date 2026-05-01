import json
import os

SNAPSHOTS_DIR = 'snapshots'

def get_total_pts(data):
    return sum(int(v) for v in data.get('pts', {}).values())

def calculate_full_day_30():
    # Финал 29-го
    f29 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-29_23-59.json')
    # Последний РЕАЛЬНЫЙ снапшот 30-го (19:16 МСК)
    f30_last_real = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_16-16.json')
    
    with open(f29, 'r') as f: d29 = json.load(f)
    with open(f30_last_real, 'r') as f: d30 = json.load(f)
    
    pts_diff = get_total_pts(d30) - get_total_pts(d29)
    rat_diff = d30.get('clanRating', 0) - d29.get('clanRating', 0)
    
    total_burned_30 = pts_diff - rat_diff
    print(f"Итоговое натуральное сгорание за 30.04 (до ночного переноса): {total_burned_30}")
    return total_burned_30

if __name__ == "__main__":
    calculate_full_day_30()
