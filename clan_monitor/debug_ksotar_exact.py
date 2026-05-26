import json, os
from datetime import datetime

path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
ksotar_id = '227408'
files = sorted([f for f in os.listdir(path) if f.startswith('points_utc_') and f.endswith('.json')])

# Анализ всей текущей недели (с 25 мая 2026)
monday = datetime(2026, 5, 25)

print(f'Полный лог изменений ksotar (ID: {ksotar_id}) с {monday.strftime("%d.%m")}:')
print('-' * 70)

last_pts = None
for f_name in files:
    try:
        ts_part = f_name.replace('points_utc_', '').replace('.json', '')
        dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
        
        # Берем данные с понедельника
        if dt >= monday:
            with open(os.path.join(path, f_name), 'r') as f:
                data = json.load(f)
                pts = data.get('pts', {}).get(ksotar_id)
                
                if pts is not None:
                    if last_pts is not None and pts != last_pts:
                        diff = pts - last_pts
                        status = "СБРОС/ВЫХОД" if abs(diff) > 1000 else "ИЗМЕНЕНИЕ"
                        print(f'{status}: {f_name} | {dt.strftime("%A, %d.%m %H:%M")} | {last_pts} -> {pts} (Δ {diff:+})')
                    last_pts = pts
    except Exception as e:
        continue
