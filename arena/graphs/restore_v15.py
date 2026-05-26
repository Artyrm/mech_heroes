import json, collections
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.patches as patches

with open('arena/squads/227408/online_history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

activity_grid = collections.defaultdict(set)
days_set = sorted(list(set(datetime.strptime(ts, '%d/%m/%Y_%H:%M:%S.%f').strftime('%Y-%m-%d') for ts in history)))
num_days = len(days_set)
grid = np.zeros((24, num_days))

date_to_col = {d: i for i, d in enumerate(days_set)}
for ts_str in history:
    dt = datetime.strptime(ts_str, '%d/%m/%Y_%H:%M:%S.%f') + timedelta(hours=3)
    grid[dt.hour, date_to_col[dt.strftime('%Y-%m-%d')]] = 1

fig, ax = plt.subplots(figsize=(num_days * 0.5 + 2, 8))

# 1. Фон (Rectangle, zorder=0) - ВОЗВРАЩАЮ ИЗ V5
for i, d in enumerate(days_set):
    if datetime.strptime(d, '%Y-%m-%d').weekday() >= 5:
        rect = patches.Rectangle((i - 0.5, -0.5), 1, 24, facecolor='red', alpha=0.3, zorder=0)
        ax.add_patch(rect)

# 2. Сетка данных (zorder=2)
ax.pcolormesh(grid, cmap='Blues', edgecolors='gray', linewidth=0.5, zorder=2)
ax.set_aspect('equal')

# 3. Риски и подписи (из V5)
ax.set_yticks(np.arange(24) + 0.5)
ax.set_yticklabels(range(24))
ax.set_xticks(np.arange(num_days) + 0.5)
ax.set_xticklabels(days_set, rotation=45, ha='right', fontsize=8)

plt.title('Активность Хоббита (MSK)')
plt.tight_layout()
plt.savefig('hobbit_final_v15_restored.png')
print('График восстановлен как hobbit_final_v15_restored.png')
