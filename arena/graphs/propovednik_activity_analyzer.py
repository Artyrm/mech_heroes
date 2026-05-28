import os, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# ==============================================================================
# PLAYER ACTIVITY ANALYZER (Generic)
# ==============================================================================

# Конфигурация для Проповедника
USER_ID = "47368"
USER_NICK = "Проповедник"
TZ_OFFSET = 3 # UTC -> MSK
PATHS = {
    "online_history": os.path.join("arena", "squads", USER_ID, "online_history.json"),
    "battles_dir": os.path.join("battle_analytics", USER_NICK),
    "holidays": os.path.join("arena", "graphs", "holidays.json"),
    "graphs_dir": os.path.join("arena", "graphs")
}

def load_data():
    online = set()
    battles = set()
    
    # 1. Online history
    if os.path.exists(PATHS["online_history"]):
        with open(PATHS["online_history"], "r", encoding="utf-8") as f:
            history = json.load(f)
            for ts in history:
                dt = datetime.strptime(ts, "%d/%m/%Y_%H:%M:%S.%f") + timedelta(hours=TZ_OFFSET)
                online.add((dt.date(), dt.hour))
    
    # 2. Battles (фильтрация по "ЗАЩИТА", т.к. лог нападений ksotar на этого игрока)
    if os.path.exists(PATHS["battles_dir"]):
        for f_name in os.listdir(PATHS["battles_dir"]):
            if f_name.startswith("battle_") and f_name.endswith(".html"):
                with open(os.path.join(PATHS["battles_dir"], f_name), 'r', encoding='utf-8') as f:
                    if "ЗАЩИТА" in f.read():
                        parts = f_name.split("_")
                        dt = datetime.strptime(f"{parts[1]}_{parts[2]}", "%Y-%m-%d_%H-%M-%S") + timedelta(hours=TZ_OFFSET)
                        battles.add((dt.date(), dt.hour))
    return online, battles

def load_holidays():
    if os.path.exists(PATHS["holidays"]):
        with open(PATHS["holidays"], "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def generate_graph():
    online, battles = load_data()
    all_known_dates = sorted(list(set([pt[0] for pt in online] + [pt[0] for pt in battles])))
    if not all_known_dates:
        print(f"Нет данных активности для {USER_NICK}")
        return
    
    min_d, max_d = all_known_dates[0], all_known_dates[-1]
    all_dates = [min_d + timedelta(days=i) for i in range((max_d - min_d).days + 1)]
    
    num_days = len(all_dates)
    date_map = {d: i for i, d in enumerate(all_dates)}
    
    grid_all = np.zeros((24, num_days))
    for d, h in online:
        if d in date_map: grid_all[h, date_map[d]] = 1
    for d, h in battles:
        if d in date_map: grid_all[h, date_map[d]] = 1

    fig, ax = plt.subplots(figsize=(num_days * 0.4 + 4, 10))
    
    # Праздники
    holidays = load_holidays()
    for i, d in enumerate(all_dates):
        if d.weekday() >= 5 or d.strftime("%Y-%m-%d") in holidays:
            ax.add_patch(patches.Rectangle((i, 0), 1, 24, facecolor='salmon', alpha=0.3, zorder=0))

    # Активность
    ax.pcolormesh(np.ma.masked_where(grid_all == 0, grid_all), cmap='Blues', vmin=0, vmax=1, zorder=1)

    # Сетка
    for i in range(num_days + 1): ax.axvline(i, color='#808080', linewidth=0.5, zorder=3)
    for i in range(25): ax.axhline(i, color='#808080', linewidth=0.5, zorder=3)

    ax.set_ylim(0, 24); ax.set_xlim(0, num_days)
    ax.set_yticks(np.arange(24) + 0.5); ax.set_yticklabels([f"{h:02d}:00" for h in range(24)])
    ax.set_xticks(np.arange(num_days) + 0.5); ax.set_xticklabels([d.strftime("%d.%m") for d in all_dates], rotation=45, ha='right', fontsize=9)
    plt.title(f'Активность игрока {USER_NICK} (Синий - любая активность)', fontsize=14, pad=20)
    plt.tight_layout()

    out_path = os.path.join(PATHS["graphs_dir"], f"{USER_NICK}_activity_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.png")
    plt.savefig(out_path, dpi=150)
    print(f'График сохранен: {out_path}')

if __name__ == "__main__":
    generate_graph()
