import json, os
from datetime import datetime
import matplotlib.pyplot as plt

path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
files = sorted([f for f in os.listdir(path) if f.startswith('points_utc_') and f.endswith('.json')])

times = []
ratings = []
monday = datetime(2026, 5, 25)

print(f'Сбор данных кланового рейтинга с {monday.strftime("%d.%m")}...')

for f_name in files:
    try:
        ts_part = f_name.replace('points_utc_', '').replace('.json', '')
        dt = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M')
        
        if dt >= monday:
            with open(os.path.join(path, f_name), 'r') as f:
                data = json.load(f)
                r = data.get('clanRating')
                if r is not None:
                    times.append(dt)
                    ratings.append(int(r))
    except: continue

if not times:
    print("Данные кланового рейтинга не найдены.")
    exit()

plt.figure(figsize=(10, 5))
plt.plot(times, ratings, marker='.', linestyle='-', color='crimson', linewidth=2)
plt.title(f'Динамика кланового рейтинга (Неделя с {monday.strftime("%d.%m")})', fontsize=14)
plt.ylabel('Рейтинг клана')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()

out_file = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\clan_rating_week.png'
plt.savefig(out_file, dpi=150)
print(f'График сохранен: {out_file}')
