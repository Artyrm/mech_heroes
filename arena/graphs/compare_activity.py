import json, os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Настройки
users = {
    "ksotar": r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\squads\227408\online_history.json',
    "hobbit": r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\squads\113012\online_history.json'
}
TZ_OFFSET = 3

def get_hourly_grid(file_path):
    activity = set()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            history = json.load(f)
            for ts in history:
                dt = datetime.strptime(ts, "%d/%m/%Y_%H:%M:%S.%f") + timedelta(hours=TZ_OFFSET)
                # Округляем до часа
                activity.add((dt.strftime("%Y-%m-%d"), dt.hour))
    return activity

# Сбор данных
grids = {}
all_dates = set()
for name, path in users.items():
    grids[name] = get_hourly_grid(path)
    all_dates.update([d[0] for d in grids[name]])

sorted_dates = sorted(list(all_dates))
date_map = {d: i for i, d in enumerate(sorted_dates)}
num_days = len(sorted_dates)

# Построение
fig, axes = plt.subplots(2, 1, figsize=(num_days * 0.4 + 4, 10))

for idx, (name, activity) in enumerate(grids.items()):
    grid = np.zeros((24, num_days))
    for d, h in activity:
        grid[h, date_map[d]] = 1
    
    ax = axes[idx]
    ax.pcolormesh(grid, cmap='Blues', edgecolors='#d0d0d0', linewidth=0.5)
    ax.set_title(f'Активность: {name}')
    ax.set_yticks(np.arange(24) + 0.5)
    ax.set_yticklabels([f"{h:02d}" for h in range(24)])
    ax.set_xticks(np.arange(num_days) + 0.5)
    ax.set_xticklabels(sorted_dates, rotation=45, ha='right')

plt.tight_layout()
out_file = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\compare_activity.png'
plt.savefig(out_file, dpi=150)
print(f'Сравнительный график сохранен: {out_file}')
