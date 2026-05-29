import os, json
from datetime import datetime
import matplotlib.pyplot as plt

# Конфигурация
USER_ID = "227408"  # ksotar
PATH_SNAPS = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
MONDAY = datetime(2026, 5, 25)

def get_data():
    files = sorted([f for f in os.listdir(PATH_SNAPS) if f.startswith('points_utc_') and f.endswith('.json')])
    times = []
    raw_pts = []
    accumulated_pts = []
    
    current_accum = 0
    last_val = 0
    
    for f_name in files:
        try:
            ts_part = f_name.replace('points_utc_', '').replace('.json', '')
            dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
            if dt < MONDAY: continue
            
            with open(os.path.join(PATH_SNAPS, f_name), 'r') as f:
                data = json.load(f)
                val = data.get('pts', {}).get(USER_ID, 0)
                
                # Реальные очки
                times.append(dt)
                raw_pts.append(val)
                
                # Накопление: считаем прирост на каждой точке
                if val > last_val:
                    current_accum += (val - last_val)
                # Если val <= last_val, это либо сброс, либо нет активности - накопление не меняем
                
                accumulated_pts.append(current_accum)
                last_val = val
        except Exception: continue
            
    return times, raw_pts, accumulated_pts

times, raw, accum = get_data()

plt.figure(figsize=(12, 6))
plt.plot(times, raw, label='Реальные очки (API)', color='red', alpha=0.5, marker='.')
plt.plot(times, accum, label='Накопленные (Point-to-Point)', color='blue', marker='.')
plt.title(f'Динамика вклада ksotar (реальные vs накопленные)', fontsize=14)
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

out = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\ksotar_compare_logic_v3.png'
plt.savefig(out, dpi=150)
print(f'График сохранен: {out}')
