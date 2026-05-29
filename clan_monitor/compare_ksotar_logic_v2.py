import os, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Конфигурация
USER_ID = "227408"  # ksotar
PATH_SNAPS = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
MONDAY = datetime(2026, 5, 25)

def get_data():
    files = sorted([f for f in os.listdir(PATH_SNAPS) if f.startswith('points_utc_') and f.endswith('.json')])
    # Группируем данные по дням
    daily_data = {}
    for f_name in files:
        try:
            ts_part = f_name.replace('points_utc_', '').replace('.json', '')
            dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
            if dt < MONDAY: continue
            
            with open(os.path.join(PATH_SNAPS, f_name), 'r') as f:
                data = json.load(f)
                val = data.get('pts', {}).get(USER_ID, 0)
                d_str = dt.strftime('%Y-%m-%d')
                if d_str not in daily_data: daily_data[d_str] = []
                daily_data[d_str].append((dt, val))
        except: continue

    times = []
    raw_pts = []
    accumulated_pts = []
    
    total_accum = 0
    prev_day_end = 0
    
    # Сортируем дни
    sorted_days = sorted(daily_data.keys())
    
    for d in sorted_days:
        day_snaps = sorted(daily_data[d], key=lambda x: x[0])
        day_vals = [v for t, v in day_snaps]
        
        # Логика бота: считаем прирост внутри дня
        # Если было падение в 0, считаем прирост после 0 как новый вклад
        day_max = max(day_vals)
        day_growth = max(0, day_max - prev_day_end)
        
        total_accum += day_growth
        
        # Записываем точки для графика
        for t, v in day_snaps:
            times.append(t)
            raw_pts.append(v)
            accumulated_pts.append(total_accum)
            
        prev_day_end = day_vals[-1]
            
    return times, raw_pts, accumulated_pts

times, raw, accum = get_data()

plt.figure(figsize=(12, 6))
plt.plot(times, raw, label='Реальные очки (API)', color='red', alpha=0.5, marker='.')
plt.plot(times, accum, label='Накопленные (Алгоритм Казначея)', color='blue', marker='.')
plt.title(f'ksotar: Реальные очки vs Алгоритмический вклад', fontsize=14)
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

out = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\ksotar_compare_logic_v2.png'
plt.savefig(out, dpi=150)
print(f'График сохранен: {out}')
