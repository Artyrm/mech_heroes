import json
import os

SNAPSHOTS_DIR = 'snapshots'

def get_total_pts(data):
    return sum(int(v) for v in data.get('pts', {}).values())

def calculate_real_burn():
    # Финал 29-го
    f29 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-29_23-59.json')
    # Первое утро 30-го
    f30_morning = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_10-25.json')
    
    if not os.path.exists(f29) or not os.path.exists(f30_morning):
        print("Ошибка: Файлы не найдены.")
        return

    with open(f29, 'r') as f: d29 = json.load(f)
    with open(f30_morning, 'r') as f: d30 = json.load(f)
    
    pts29 = get_total_pts(d29)
    pts30 = get_total_pts(d30)
    rat29 = d29.get('clanRating', 0)
    rat30 = d30.get('clanRating', 0)
    
    growth_pts = pts30 - pts29
    growth_rat = rat30 - rat29
    burn = growth_pts - growth_rat
    
    print(f"--- СТАТИСТИКА НА УТРО 30.04 ---")
    print(f"Прирост очков игроков: {growth_pts}")
    print(f"Прирост рейтинга клана: {growth_rat}")
    print(f"РЕАЛЬНО СГОРЕЛО: {burn}")

if __name__ == "__main__":
    calculate_real_burn()
