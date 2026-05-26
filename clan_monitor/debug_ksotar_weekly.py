import json, os
from datetime import datetime

path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
files = sorted([f for f in os.listdir(path) if f.startswith('points_utc_') and f.endswith('.json')])

# Найдем ID ksotar
ksotar_id = "227408" # Как показал предыдущий запуск

print(f'Анализ сбросов ksotar (ID: {ksotar_id}) по неделям (с понедельника):')
print('-' * 60)

last_pts = None
for f_name in files:
    try:
        # Извлекаем дату из имени файла
        ts_part = f_name.replace('points_utc_', '').replace('.json', '')
        dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
        
        with open(os.path.join(path, f_name), 'r') as f:
            data = json.load(f)
            pts = data.get('pts', {}).get(ksotar_id)
            if pts is None: continue
            
            # Определяем неделю (понедельник=0)
            week_num = dt.strftime('%W')
            weekday = dt.strftime('%A')
            
            # Ищем падение более чем на 5000
            if last_pts is not None and pts < last_pts - 5000:
                print(f'СБРОС: {f_name} | День: {dt.strftime("%A, %d.%m")} | {last_pts} -> {pts}')
            
            last_pts = pts
    except:
        continue
