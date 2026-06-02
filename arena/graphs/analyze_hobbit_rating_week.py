import json, os
from datetime import datetime
import matplotlib.pyplot as plt

USER_ID = 113012
snapshots_dir = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\snapshots'
files = sorted([f for f in os.listdir(snapshots_dir) if f.startswith('arena_') and f.endswith('.json')])

times = []
ratings = []
monday = datetime(2026, 5, 25)

print(f'Сбор данных рейтинга для Хоббита ({USER_ID}) с {monday.strftime("%d.%m")}...')

for f_name in files:
    try:
        # Expected format: arena_2026-04-29T09-27-19.json
        ts_part = f_name.replace('arena_', '').replace('.json', '')
        dt = datetime.strptime(ts_part, '%Y-%m-%dT%H-%M-%S')
        
        if dt >= monday:
            with open(os.path.join(snapshots_dir, f_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Arena snapshot structure: {'players': [{'userID': 113012, 'rating': '4195'}, ...]}
                players = data.get('players', [])
                for p in players:
                    if p.get('userID') == USER_ID:
                        times.append(dt)
                        ratings.append(int(p.get('rating', 0)))
                        break
    except Exception as e:
        print(f"Error processing {f_name}: {e}")
        continue

if not times:
    print("Данные не найдены.")
    exit()

plt.figure(figsize=(10, 5))
plt.plot(times, ratings, marker='.', linestyle='-', color='orange', linewidth=2)
plt.title(f'Траектория рейтинга Хоббита (Неделя с {monday.strftime("%d.%m")})', fontsize=14)
plt.ylabel('Рейтинг')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()

out_file = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\hobbit_rating_week.png'
plt.savefig(out_file, dpi=150)
print(f'График сохранен: {out_file}')
