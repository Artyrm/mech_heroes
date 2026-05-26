import os, json, collections
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# Пути
h_path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\squads\227408\online_history.json'
b_path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\battle_analytics\Хоббит'
out_path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\hobbit_final_v22_rebuilt.png'

# 1. Сбор данных
activity_points = set()

# Из online_history (UTC -> MSK)
with open(h_path, 'r', encoding='utf-8') as f:
    history = json.load(f)
for ts_str in history:
    dt = datetime.strptime(ts_str, '%d/%m/%Y_%H:%M:%S.%f') + timedelta(hours=3)
    activity_points.add(dt)

# Из файлов боев (Имя файла содержит UTC -> MSK)
for f_name in os.listdir(b_path):
    if f_name.startswith('battle_') and f_name.endswith('.html'):
        try:
            # battle_2026-05-19_14-13-16_0090.html
            parts = f_name.split('_')
            ts_part = parts[1] + '_' + parts[2]
            dt_b = datetime.strptime(ts_part, '%Y-%m-%d_%H-%M-%S') + timedelta(hours=3)
            activity_points.add(dt_b)
        except:
            pass

# 2. Подготовка сетки
days_set = sorted(list(set(dt.strftime('%Y-%m-%d') for dt in activity_points)))
num_days = len(days_set)
grid = np.zeros((24, num_days))

date_to_col = {d: i for i, d in enumerate(days_set)}
for dt in activity_points:
    grid[dt.hour, date_to_col[dt.strftime('%Y-%m-%d')]] = 1

# 3. Визуализация
fig, ax = plt.subplots(figsize=(num_days * 0.5 + 4, 10))

# Выходные (фон)
for i, d in enumerate(days_set):
    if datetime.strptime(d, '%Y-%m-%d').weekday() >= 5:
        rect = patches.Rectangle((i - 0.5, -0.5), 1, 24, facecolor='salmon', alpha=0.2, zorder=0)
        ax.add_patch(rect)

# Сетка данных
im = ax.pcolormesh(grid, cmap='YlGnBu', edgecolors='white', linewidth=0.5, zorder=2)
ax.set_aspect('equal')

# Оформление
ax.set_yticks(np.arange(24) + 0.5)
ax.set_yticklabels([f'{h:02d}:00' for h in range(24)])
ax.set_xticks(np.arange(num_days) + 0.5)
ax.set_xticklabels(days_set, rotation=45, ha='right', fontsize=9)

plt.title('Активность Хоббита (Online + Battles, MSK)', fontsize=16, pad=20)
plt.xlabel('Дата', fontsize=12)
plt.ylabel('Час суток (MSK)', fontsize=12)

plt.grid(False)
plt.tight_layout()
plt.savefig(out_path, dpi=150)
print(f'График успешно создан: {out_path}')
