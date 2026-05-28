import os, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# ==============================================================================
# OVERLAP ANALYZER - HISTORY
# ==============================================================================

USERS = {"ksotar": "227408", "hobbit": "113012"}
TZ_OFFSET = 3 # UTC -> MSK
PATHS = {
    "holidays": os.path.join("arena", "graphs", "holidays.json"),
    "graphs_dir": os.path.join("arena", "graphs")
}

def load_activity(user_id):
    path = os.path.join("arena", "squads", user_id, "online_history.json")
    points = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
            for ts_str in history:
                dt = datetime.strptime(ts_str, "%d/%m/%Y_%H:%M:%S.%f") + timedelta(hours=TZ_OFFSET)
                points.add((dt.date(), dt.hour))
    return points

def load_holidays():
    if os.path.exists(PATHS["holidays"]):
        with open(PATHS["holidays"], "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# 1. Загрузка данных
ksotar_pts = load_activity(USERS["ksotar"])
hobbit_pts = load_activity(USERS["hobbit"])

# Используем ВСЕ даты, которые есть в логах обоих игроков
all_known_dates = sorted(list(set([pt[0] for pt in ksotar_pts] + [pt[0] for pt in hobbit_pts])))
min_date, max_date = all_known_dates[0], all_known_dates[-1]

# Генерируем полный диапазон дат (от первой до последней записи)
all_dates = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
date_map = {d: i for i, d in enumerate(all_dates)}
num_days = len(all_dates)

# 2. Матрицы пересечений
overlap = np.zeros((24, num_days))
for d, h in ksotar_pts:
    if (d, h) in hobbit_pts:
        overlap[h, date_map[d]] = 1

overlap_masked = np.ma.masked_where(overlap == 0, overlap)
holidays = load_holidays()

# 3. Визуализация
fig, ax = plt.subplots(figsize=(num_days * 0.4 + 4, 10))

# Слой 0: Выходные и праздники (Красный)
for i, d in enumerate(all_dates):
    if d.weekday() >= 5 or d.strftime("%Y-%m-%d") in holidays:
        rect = patches.Rectangle((i, 0), 1, 24, facecolor='salmon', alpha=0.3, zorder=0)
        ax.add_patch(rect)

# Слой 1: Пересечения (Фиолетовый)
ax.pcolormesh(overlap_masked, cmap='Purples', vmin=0, vmax=1, zorder=1)

# Слой 3: Сетка (поверх всего)
for i in range(num_days + 1): ax.axvline(i, color='#808080', linewidth=0.5, zorder=3)
for i in range(25): ax.axhline(i, color='#808080', linewidth=0.5, zorder=3)

# Оформление
ax.set_ylim(0, 24)
ax.set_xlim(0, num_days)
ax.set_yticks(np.arange(24) + 0.5)
ax.set_yticklabels([f"{h:02d}:00" for h in range(24)])
ax.set_xticks(np.arange(num_days) + 0.5)
ax.set_xticklabels([d.strftime("%d.%m") for d in all_dates], rotation=45, ha='right', fontsize=9)

plt.title('Часы совместной активности (ksotar & Хоббит)', fontsize=16, pad=20)
plt.ylabel('Час суток', fontsize=12)
plt.tight_layout()

os.makedirs(PATHS["graphs_dir"], exist_ok=True)
out_path = os.path.join(PATHS["graphs_dir"], f"overlap_history_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.png")
plt.savefig(out_path, dpi=150)
print(f'График сохранен: {out_path}')
