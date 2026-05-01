import json
import os
from datetime import datetime, timedelta, timezone

SNAPSHOTS_DIR = 'snapshots'

def interpolate():
    # Фактические точки разрыва (UTC)
    # 19:16 MSK = 16:16 UTC
    # 03:56 MSK = 00:56 UTC (следующего дня)
    f_start = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_16-16.json')
    f_end = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    
    if not os.path.exists(f_start) or not os.path.exists(f_end):
        print("ОШИБКА: Снапшоты для интерполяции не найдены.")
        return

    with open(f_start, 'r') as f: d_start = json.load(f)
    with open(f_end, 'r') as f: d_end = json.load(f)
    
    # 16:16 UTC to 00:56 UTC (next day) is 8h 40m = 520 minutes
    # Game reset is at 00:00 UTC. 
    # From 16:16 UTC to 00:00 UTC is 7h 44m = 464 minutes.
    ratio = 464 / 520.0
    
    new_pts = {}
    pts_start = d_start['pts']
    pts_end = d_end['pts']
    
    # Собираем всех игроков из обоих снапшотов
    all_uids = set(pts_start.keys()) | set(pts_end.keys())
    
    for uid in all_uids:
        v1 = pts_start.get(uid, pts_end.get(uid, 0))
        v2 = pts_end.get(uid, v1)
        # Линейная интерполяция
        val = int(v1 + (v2 - v1) * ratio)
        new_pts[uid] = val
        
    r1 = d_start.get('clanRating', 0)
    r2 = d_end.get('clanRating', r1)
    new_rating = int(r1 + (r2 - r1) * ratio)
    
    # Сохраняем как снапшот на 23:59 UTC (финал дня по серверу)
    new_snap = {
        "pts": new_pts,
        "clanRating": new_rating
    }
    
    target_file = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_23-59.json')
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(new_snap, f, ensure_ascii=False)
    
    print(f"Успех: Создан интерполированный снапшот {target_file}")
    print(f"Коэффициент переноса на вчера: {ratio:.2%}")

if __name__ == "__main__":
    interpolate()
