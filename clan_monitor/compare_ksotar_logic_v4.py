import os, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

USER_ID = "227408"  # ksotar
PATH_SNAPS = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
PATH_ADJ = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\manual_adjustments.json'
MONDAY = datetime(2026, 5, 25)

def get_data():
    with open(PATH_ADJ, 'r', encoding='utf-8') as f:
        adj = json.load(f)

    files = sorted([f for f in os.listdir(PATH_SNAPS) if f.startswith('points_utc_') and f.endswith('.json')])
    times = []
    raw_pts = []
    accumulated_pts = []
    
    total_accum = 0
    last_val = 0
    
    for f_name in files:
        try:
            ts_part = f_name.replace('points_utc_', '').replace('.json', '')
            dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
            if dt < MONDAY: continue
            
            with open(os.path.join(PATH_SNAPS, f_name), 'r') as f:
                data = json.load(f)
                val = data.get('pts', {}).get(USER_ID, 0)
                
                # Добавляем корректировку
                day_str = dt.strftime('%Y-%m-%d')
                manual_val = 0
                if day_str in adj and USER_ID in adj[day_str]:
                    manual_val = adj[day_str][USER_ID][-1]
                
                # В качестве реального значения берем max между снапшотом и корректировкой
                val = max(val, manual_val)
                
                times.append(dt)
                raw_pts.append(val)
                
                # Логика: если val >= last_val, прибавляем дельту.
                # Если произошел сброс (val < last_val), мы считаем, что игрок заработал val очков 
                # сверх того, что уже было накоплено до сброса.
                if val >= last_val:
                    total_accum += (val - last_val)
                else:
                    # При сбросе в 0 или ниже, мы считаем что все очки, которые 
                    # игрок заработал *после* сброса, должны быть приплюсованы к total_accum.
                    # last_val обновляется, чтобы в следующей итерации считать разницу.
                    total_accum += val
                
                accumulated_pts.append(total_accum)
                last_val = val
        except Exception as e: continue
            
    return times, raw_pts, accumulated_pts

times, raw, accum = get_data()

plt.figure(figsize=(12, 6))
plt.plot(times, raw, label='Реальные очки (API + Adj)', color='red', alpha=0.5, marker='.')
plt.plot(times, accum, label='Честное накопление', color='blue', marker='.')
plt.title(f'Динамика вклада ksotar (с учетом правок и сбросов)', fontsize=14)
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

out = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\ksotar_compare_logic_v4.png'
plt.savefig(out, dpi=150)
print(f'График сохранен: {out}')
